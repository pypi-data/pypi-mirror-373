"""Weather server request handler mixin."""

import time
import threading
import traceback
from datetime import datetime

from WIPCommonPy.packet import (
    LocationRequest,
    LocationResponse,
    QueryRequest,
    QueryResponse,
    ReportRequest,
    ReportResponse,
    ErrorResponse,
    ExtendedField,
)
from WIPCommonPy.packet.debug.debug_logger import PacketDebugLogger
from WIPCommonPy.utils.log_config import UnifiedLogFormatter


class WeatherRequestHandlers:
    """Mixin providing handler implementations for WeatherServer."""

    def __init__(self, *args, **kwargs):
        """Initialize debug logger for weather server handlers."""
        super().__init__(*args, **kwargs)
        self.packet_debug_logger = PacketDebugLogger("WeatherServer")

    # ----------------------
    # Internal small helpers
    # ----------------------
    def _extract_coordinates(self, obj):
        """Safely extract (lat, lon) from packet or its ex_field.

        Returns (lat, lon) or (None, None).
        """
        lat = None
        lon = None
        try:
            if hasattr(obj, "get_coordinates") and callable(obj.get_coordinates):
                coords = obj.get_coordinates()
                if coords:
                    lat, lon = coords
            if (lat is None or lon is None) and hasattr(obj, "ex_field") and obj.ex_field:
                # ExtendedField may support dict-like access
                try:
                    lat = lat if lat is not None else obj.ex_field.get("latitude")
                    lon = lon if lon is not None else obj.ex_field.get("longitude")
                except Exception:
                    # Fallback to attribute access
                    lat = lat if lat is not None else getattr(obj.ex_field, "latitude", None)
                    lon = lon if lon is not None else getattr(obj.ex_field, "longitude", None)
        except Exception:
            pass
        return lat, lon

    def _ensure_ex_field(self, packet, set_flag=True):
        """Ensure packet.ex_field exists and optionally set ex_flag=1.

        Returns the ExtendedField instance.
        """
        if not hasattr(packet, "ex_field") or packet.ex_field is None:
            packet.ex_field = ExtendedField()
        if set_flag and hasattr(packet, "ex_flag"):
            packet.ex_flag = 1
        return packet.ex_field

    def _set_source(self, packet, source_info):
        """Ensure ex_field exists and set source tuple."""
        ex = self._ensure_ex_field(packet, set_flag=True)
        ex.source = source_info

    def _get_source_from_request(self, request):
        """Return (host, port) tuple if present in request.ex_field.source, else None."""
        try:
            if hasattr(request, "ex_field") and request.ex_field and request.ex_field.contains("source"):
                cand = request.ex_field.source
                if isinstance(cand, tuple) and len(cand) == 2:
                    return cand
        except Exception:
            pass
        return None

    def _validate_source_info(self, source_info):
        """Accept tuple or "host:port" string. Return (host, int_port) or raise ValueError."""
        if not source_info:
            raise ValueError("missing source_info")
        if isinstance(source_info, tuple) and len(source_info) == 2:
            host, port = source_info
            port = int(port)
            if not (0 < port <= 65535):
                raise ValueError("Invalid port number")
            return host, port
        if isinstance(source_info, str) and ":" in source_info:
            host, port_str = source_info.split(":", 1)
            port = int(port_str)
            if not (0 < port <= 65535):
                raise ValueError("Invalid port number")
            return host, port
        raise ValueError(f"invalid source_info format: {source_info}")

    def _strip_source_from_ex_field(self, packet):
        """Remove source from ex_field and normalize flag when empty."""
        try:
            if hasattr(packet, "ex_field") and packet.ex_field:
                if hasattr(packet.ex_field, "remove"):
                    packet.ex_field.remove("source")
                # Normalize flag if empty
                if hasattr(packet.ex_field, "is_empty") and packet.ex_field.is_empty():
                    setattr(packet.ex_field, "flag", 0)
        except Exception:
            pass

    def _add_auth_hash(self, packet, passphrase_key):
        """Add auth hash into ex_field if auth is enabled.

        Returns True on success or when auth disabled; False on failure.
        """
        if not getattr(self, "auth_enabled", False):
            return True
        try:
            from WIPCommonPy.utils.auth import WIPAuth

            passphrase = self.passphrases[passphrase_key]
            auth_hash = WIPAuth.calculate_auth_hash(
                packet.packet_id, packet.timestamp, passphrase
            )
            ex = self._ensure_ex_field(packet, set_flag=True)
            ex.auth_hash = auth_hash.hex()
            return True
        except Exception:
            return False

    def _send_error_to_dest(self, code, packet_id, dest):
        """Build and send ErrorResponse with ex_field.source set to dest, if valid."""
        try:
            error_response = ErrorResponse(
                version=self.version,
                packet_id=packet_id,
                error_code=code,
                timestamp=int(datetime.now().timestamp()),
            )
            try:
                valid = self._validate_source_info(dest)
            except Exception:
                valid = None
            if valid:
                error_response.ex_field.source = valid
                self.sock.sendto(error_response.to_bytes(), valid)
        except Exception:
            # Swallow to avoid masking original errors
            pass

    def _send_error_to_request_source(self, code, packet_id, request):
        """Send ErrorResponse to request.ex_field.source if available."""
        dest = self._get_source_from_request(request)
        if dest:
            self._send_error_to_dest(code, packet_id, dest)

    def _send_and_check(self, data, host, port):
        """Send using send_udp_packet and validate size."""
        bytes_sent = self.send_udp_packet(data, host, port)
        if bytes_sent != len(data):
            raise RuntimeError(
                f"404: 不正なパケット長: (expected: {len(data)}, sent: {bytes_sent})"
            )
        return bytes_sent

    def _sendto_and_check(self, data, dest_addr):
        """Send using sock.sendto and validate size."""
        bytes_sent = self.sock.sendto(data, dest_addr)
        if bytes_sent != len(data):
            raise RuntimeError(
                f"送信バイト数不一致: {bytes_sent}/{len(data)}"
            )
        return bytes_sent

    def _handle_location_request(self, request, addr):
        """座標解決リクエストの処理（Type 0・改良版）"""
        source_info = (addr[0], addr[1])  # タプル形式で保持
        try:
            # location_clientのキャッシュを使用してエリアコード取得を試行（ネットワークリクエストなし）
            coords = (
                request.get_coordinates()
                if hasattr(request, "get_coordinates")
                and callable(request.get_coordinates)
                else None
            )
            if coords:
                lat, long = coords

                # キャッシュのみをチェック（ネットワークリクエストは送信しない）
                cached_area_code = self.location_client.get_cached_area_code(lat, long)

                if cached_area_code:

                    try:
                        query_request = QueryRequest.create_query_request(
                            area_code=cached_area_code,
                            packet_id=request.packet_id,
                            day=request.day,
                            weather=bool(request.weather_flag),
                            temperature=bool(request.temperature_flag),
                            precipitation_prob=bool(request.pop_flag),
                            alert=bool(request.alert_flag),
                            disaster=bool(request.disaster_flag),
                            source=source_info,
                            version=self.version,
                        )

                        # 座標情報を拡張フィールドに追加
                        if (
                            not hasattr(query_request, "ex_field")
                            or query_request.ex_field is None
                        ):
                            query_request.ex_field = ExtendedField()
                        query_request.ex_field.latitude = lat
                        query_request.ex_field.longitude = long
                        query_request.ex_flag = 1

                        # _handle_query_requestに処理を移譲
                        return self._handle_query_request(query_request, addr)

                    except Exception as e:
                        print(f"キャッシュデータの処理中にエラーが発生しました: {e}")
                        self.logger.error(
                            f"キャッシュデータの処理中にエラーが発生しました: {e}"
                        )
                        self.logger.debug(traceback.format_exc())
                        # エラーが発生した場合は通常処理を続行
            else:
                # 拡張フィールドから直接座標を取得
                lat = (
                    request.ex_field.get("latitude")
                    if hasattr(request, "ex_field") and request.ex_field
                    else None
                )
                long = (
                    request.ex_field.get("longitude")
                    if hasattr(request, "ex_field") and request.ex_field
                    else None
                )

                if lat is None or long is None:
                    self.logger.debug(
                        f"[{self.server_name}] ❌ 座標情報が取得できません - location_serverに転送"
                    )

            # 既存のLocationRequestをそのまま使用し、必要に応じて拡張フィールドのみ更新
            location_request = request

            # 座標情報を取得
            coords = (
                request.get_coordinates()
                if hasattr(request, "get_coordinates")
                and callable(request.get_coordinates)
                else None
            )
            if coords:
                lat, long = coords
            else:
                # 拡張フィールドから直接座標を取得
                lat = (
                    request.ex_field.get("latitude")
                    if hasattr(request, "ex_field") and request.ex_field
                    else None
                )
                long = (
                    request.ex_field.get("longitude")
                    if hasattr(request, "ex_field") and request.ex_field
                    else None
                )

            # 拡張フィールドを確実に初期化（既存のものがあっても新規作成）
            location_request.ex_field = ExtendedField()

            # 座標情報を拡張フィールドに追加
            if lat is not None and long is not None:
                location_request.ex_field.latitude = lat
                location_request.ex_field.longitude = long

            # source情報を追加
            location_request.ex_field.source = source_info
            location_request.ex_flag = 1

            # 認証が有効な場合は認証ハッシュを追加
            if not self._add_auth_hash(location_request, "location_server"):
                self._send_error_to_request_source(401, request.packet_id, request)
                return

            # Location Resolverに転送
            packet_data = location_request.to_bytes()

            # メインソケットを使用して送信
            try:
                self._send_and_check(
                    packet_data,
                    self.location_resolver_host,
                    self.location_resolver_port,
                )
            except Exception as e:
                self.logger.debug(traceback.format_exc())
                self._send_error_to_request_source(410, request.packet_id, request)
                return

        except Exception as e:
            print(
                f"530: [{self.server_name}] 位置情報リクエストの処理中にエラーが発生しました: {e}"
            )
            self.logger.debug(traceback.format_exc())
            # ErrorResponseを作成して返す
            self._send_error_to_request_source(530, request.packet_id, request)
            return

    def _handle_location_response(self, data, addr):
        """座標解決レスポンスの処理（Type 1・改良版）"""
        start_time = time.time()
        try:
            # 専用クラスでレスポンスをパース
            response = LocationResponse.from_bytes(data)

            lat, long = response.get_coordinates()

            # location_serverからのレスポンスでlocation_clientのキャッシュを手動更新
            if response.is_valid():
                area_code = response.get_area_code()
                if area_code and lat is not None and long is not None:
                    # location_clientのキャッシュを適切なpublicメソッドで更新
                    self.location_client.set_cached_area_code(lat, long, area_code)

            # query_clientのキャッシュを使用してクエリを実行
            try:
                weather_data = self.query_client.get_weather_data(
                    area_code=response.area_code,
                    weather=bool(response.weather_flag),
                    temperature=bool(response.temperature_flag),
                    precipitation_prob=bool(response.pop_flag),
                    alert=bool(response.alert_flag),
                    disaster=bool(response.disaster_flag),
                    day=response.day,
                    use_cache=True,
                    timeout=10.0,
                )

                if weather_data and "error" not in weather_data:
                    # query_clientから直接データを取得できた場合

                    # 拡張フィールドの準備
                    ex_field_data = {}
                    if lat and long:
                        ex_field_data["latitude"] = lat
                        ex_field_data["longitude"] = long

                    # alertとdisasterのデータをキャッシュから取得して拡張フィールドに追加
                    if response.alert_flag and "alert" in weather_data:
                        ex_field_data["alert"] = weather_data["alert"]
                    if response.disaster_flag and "disaster" in weather_data:
                        ex_field_data["disaster"] = weather_data["disaster"]

                    # QueryResponseを作成
                    query_response = QueryResponse(
                        version=self.version,
                        packet_id=response.packet_id,
                        type=3,  # 気象データレスポンス
                        weather_flag=response.weather_flag,
                        temperature_flag=response.temperature_flag,
                        pop_flag=response.pop_flag,
                        alert_flag=response.alert_flag,
                        disaster_flag=response.disaster_flag,
                        ex_flag=1 if ex_field_data else 0,
                        day=response.day,
                        timestamp=int(datetime.now().timestamp()),
                        area_code=response.area_code,
                        weather_code=weather_data.get("weather_code", "0000"),
                        temperature=weather_data.get("temperature", 0)
                        + 100,  # パケット形式に変換（+100）
                        pop=weather_data.get("precipitation_prob", 0),
                        ex_field=ex_field_data if ex_field_data else None,
                    )

                    # レスポンスを送信
                    response_data = query_response.to_bytes()
                    source_info = response.get_source_info()

                    if source_info:
                        # source_infoがタプル/文字列の双方に対応
                        host, port = self._validate_source_info(source_info)
                        source_addr = (host, port)

                        self._sendto_and_check(response_data, source_addr)

                        # 統一されたデバッグ出力を追加
                        execution_time = time.time() - start_time
                        debug_data = {
                            "area_code": response.area_code,
                            "timestamp": response.timestamp,
                            "weather_code": weather_data.get("weather_code", "0000"),
                            "temperature": weather_data.get("temperature", 0),
                            "precipitation_prob": weather_data.get(
                                "precipitation_prob", 0
                            ),
                            "alert": weather_data.get("alert", []),
                            "disaster": weather_data.get("disaster", []),
                        }
                        self.packet_debug_logger.log_unified_packet_received(
                            "Location response to query conversion",
                            execution_time,
                            debug_data,
                        )

                        return  # query_clientキャッシュヒット/成功時はここで終了
                    raise RuntimeError("source情報が見つかりません")
            except Exception as e:
                pass  # 通常のクエリサーバ転送にフォールバック

            query_request = QueryRequest.from_location_response(response)

            # 認証が有効な場合は認証ハッシュを追加
            if not self._add_auth_hash(query_request, "query_server"):
                # 認証ハッシュ追加に失敗した場合はエラーレスポンスを返す
                src = response.get_source_info()
                try:
                    host, port = self._validate_source_info(src)
                    self._send_error_to_dest(401, response.packet_id, (host, port))
                except Exception:
                    pass
                return

            # Query Generatorに送信
            packet_data = query_request.to_bytes()

            # メインソケットを使用して送信
            self._send_and_check(
                packet_data, self.query_generator_host, self.query_generator_port
            )

        except Exception as e:
            print(
                f"107: [{self.server_name}] 位置情報レスポンスの処理中にエラーが発生しました: {e}"
            )
            self.logger.debug(traceback.format_exc())
            try:
                host, port = self._validate_source_info(response.get_source_info())
                self._send_error_to_dest(107, response.packet_id, (host, port))
            except Exception:
                print("sourceが不正なためエラーパケットを送信できません")
            return

    def _handle_query_request(self, request, addr):
        """気象データリクエストの処理（Type 2・改良版）"""
        start_time = time.time()
        try:
            source_info = (addr[0], addr[1])  # タプル形式で保持

            # query_clientのキャッシュを使用してクエリを実行
            try:
                weather_data = self.query_client.get_weather_data(
                    area_code=request.area_code,
                    weather=bool(request.weather_flag),
                    temperature=bool(request.temperature_flag),
                    precipitation_prob=bool(request.pop_flag),
                    alert=bool(request.alert_flag),
                    disaster=bool(request.disaster_flag),
                    day=request.day,
                    use_cache=True,
                    timeout=10.0,
                )

                if weather_data and "error" not in weather_data:
                    # query_clientから直接データを取得できた場合

                    # requestから座標情報を取得
                    coords = (
                        request.get_coordinates()
                        if hasattr(request, "get_coordinates")
                        else (None, None)
                    )
                    req_lat, req_long = coords if coords else (None, None)

                    # 拡張フィールドの準備
                    ex_field_data = {}
                    if req_lat and req_long:
                        ex_field_data["latitude"] = req_lat
                        ex_field_data["longitude"] = req_long

                    # alertとdisasterのデータをキャッシュから取得して拡張フィールドに追加
                    if request.alert_flag and "alert" in weather_data:
                        ex_field_data["alert"] = weather_data["alert"]
                    if request.disaster_flag and "disaster" in weather_data:
                        ex_field_data["disaster"] = weather_data["disaster"]

                    # QueryResponseを作成
                    query_response = QueryResponse(
                        version=self.version,
                        packet_id=request.packet_id,
                        type=3,  # 気象データレスポンス
                        weather_flag=request.weather_flag,
                        temperature_flag=request.temperature_flag,
                        pop_flag=request.pop_flag,
                        alert_flag=request.alert_flag,
                        disaster_flag=request.disaster_flag,
                        ex_flag=1 if ex_field_data else 0,
                        day=request.day,
                        timestamp=int(datetime.now().timestamp()),
                        area_code=request.area_code,
                        weather_code=weather_data.get("weather_code", "0000"),
                        temperature=weather_data.get("temperature", 0)
                        + 100,  # パケット形式に変換（+100）
                        pop=weather_data.get("precipitation_prob", 0),
                        ex_field=ex_field_data if ex_field_data else None,
                    )

                    response_data = query_response.to_bytes()
                    self.sock.sendto(response_data, addr)

                    # 統一されたデバッグ出力を追加
                    execution_time = time.time() - start_time
                    debug_data = {
                        "area_code": request.area_code,
                        "timestamp": int(datetime.now().timestamp()),
                        "weather_code": weather_data.get("weather_code", "0000"),
                        "temperature": weather_data.get("temperature", 0),
                        "precipitation_prob": weather_data.get("precipitation_prob", 0),
                        "alert": weather_data.get("alert", []),
                        "disaster": weather_data.get("disaster", []),
                    }
                    self.packet_debug_logger.log_unified_packet_received(
                        "Direct query request", execution_time, debug_data
                    )

                    return  # query_clientキャッシュヒット/成功時はここで終了
            except Exception as e:
                pass  # 通常のクエリサーバ転送にフォールバック

            # 既にQueryRequestの場合は、source情報を追加し、認証付与
            query_request = request
            self._set_source(query_request, source_info)

            # 認証ハッシュを付与（失敗時は401エラー送信）
            if not self._add_auth_hash(query_request, "query_server"):
                self._send_error_to_request_source(401, request.packet_id, request)
                return

            # Query Generatorに転送
            packet_data = query_request.to_bytes()

            # メインソケットを使用して送信
            try:
                self._send_and_check(
                    packet_data, self.query_generator_host, self.query_generator_port
                )
            except Exception as e:
                print(
                    f"クエリリクエストの転送に失敗しました: {self.query_generator_host}:{self.query_generator_port} - {str(e)}"
                )
                self.logger.debug(traceback.format_exc())
                # エラーレスポンスを送信
                self._send_error_to_request_source(420, request.packet_id, request)
                return

        except Exception as e:
            print(f"420: クエリサーバが見つからない: {e}")
            self.logger.debug(traceback.format_exc())
            # ErrorResponseを作成して返す
            self._send_error_to_request_source(420, request.packet_id, request)
            return

    def _handle_query_response(self, data, addr):
        """気象データレスポンスの処理（Type 3・改良版）"""
        start_time = time.time()
        try:
            # 専用クラスでレスポンスをパース
            response = QueryResponse.from_bytes(data)

            # 専用クラスのメソッドでsource情報を取得
            source_info = response.get_source_info()
            if not source_info:
                print(
                    f"530: [{self.server_name}] 処理エラー: 天気レスポンスに送信元情報がありません"
                )
                if hasattr(response, "ex_field"):
                    self.logger.debug(
                        f"  ex_field の内容: {response.ex_field.to_dict()}"
                    )
                return

            # source情報の検証と正規化
            try:
                host, port = self._validate_source_info(source_info)
                dest_addr = (host, port)
            except Exception:
                print(f"[{self.server_name}] 不正なsource_info形式: {source_info}")
                return

            # source情報を変数に格納したので拡張フィールドから削除（共通ヘルパー）
            self._strip_source_from_ex_field(response)

            try:
                response.version = self.version  # バージョンを正規化
                final_data = response.to_bytes()

                # 元のクライアントに送信
                try:
                    self._sendto_and_check(final_data, dest_addr)

                    # 統一されたデバッグ出力を追加
                    execution_time = time.time() - start_time
                    debug_data = {
                        "area_code": response.area_code,
                        "timestamp": response.timestamp,
                        "weather_code": response.weather_code,
                        "temperature": response.temperature
                        - 100,  # パケット形式から実際の温度に変換
                        "precipitation_prob": response.pop,
                        "alert": (
                            response.ex_field.get("alert", [])
                            if response.ex_field
                            else []
                        ),
                        "disaster": (
                            response.ex_field.get("disaster", [])
                            if response.ex_field
                            else []
                        ),
                    }
                    self.packet_debug_logger.log_unified_packet_received(
                        "Query response forwarding", execution_time, debug_data
                    )

                except Exception as e:
                    self.logger.debug(traceback.format_exc())
                    # ErrorResponseを作成して返す
                    self._send_error_to_dest(530, response.packet_id, dest_addr)
                    raise RuntimeError(
                        f"気象サーバでの処理エラー: クライアントへの転送に失敗 {str(e)}"
                    )

            except Exception as conv_e:
                print(f"530: 気象サーバでの処理エラー: {conv_e}")
                self.logger.debug(traceback.format_exc())
                # ErrorResponseを作成して返す
                self._send_error_to_dest(530, response.packet_id, dest_addr)
                return

        except Exception as e:
            print(f"530: [{self.server_name}] 基本エラー: リクエスト処理失敗: {e}")
            self.logger.debug(traceback.format_exc())
            # ErrorResponseを作成して返す
            self._send_error_to_dest(530, response.packet_id, dest_addr)
            return

    def _handle_error_packet(self, request, addr):
        """エラーパケットの処理（Type 7）"""
        try:
            # 拡張フィールドからsourceを取得
            if request.ex_field and request.ex_field.contains("source"):
                source = request.ex_field.source
                try:
                    dest_addr = self._validate_source_info(source)
                except Exception:
                    print(
                        f"[{self.server_name}] 不正なsource形式: {source} (type: {type(source)})"
                    )
                    return
                # エラーパケットを送信（長さ検証付き）
                self._sendto_and_check(request.to_bytes(), dest_addr)
            else:
                print(
                    f"[{self.server_name}] エラー: エラーパケットにsourceが含まれていません"
                )

        except Exception as e:
            print(
                f"[{self.server_name}] エラーパケット処理中にエラーが発生しました: {e}"
            )
            self.logger.debug(traceback.format_exc())
            # ErrorResponseを作成して返す
            self._send_error_to_request_source(530, request.packet_id, request)
            return

    def _handle_report_request(self, request, addr):
        """データレポートリクエストの処理（Type 4）"""
        try:
            source_info = (addr[0], addr[1])  # タプル形式で保持

            # ReportRequestにsource情報を追加（強化版）
            self._set_source(request, source_info)

            # 認証が有効な場合は認証ハッシュを追加
            if not self._add_auth_hash(request, "report_server"):
                # 認証ハッシュ追加に失敗した場合はエラーレスポンスを返す
                self._send_error_to_request_source(401, request.packet_id, request)
                return

            # レポートサーバーに転送
            packet_data = request.to_bytes()

            try:
                self._send_and_check(
                    packet_data, self.report_server_host, self.report_server_port
                )
            except Exception as e:
                print(
                    f"レポートリクエストの転送に失敗しました: {self.report_server_host}:{self.report_server_port} - {str(e)}"
                )
                self.logger.debug(traceback.format_exc())
                # ErrorResponseを作成して返す
                self._send_error_to_request_source(420, request.packet_id, request)
                return

        except Exception as e:
            print(
                f"530: [{self.server_name}] レポートリクエストの処理中にエラーが発生しました: {e}"
            )
            self.logger.debug(traceback.format_exc())
            # ErrorResponseを作成して返す
            self._send_error_to_request_source(530, request.packet_id, request)
            return

    def _handle_report_response(self, data, addr):
        """データレポートレスポンスの処理（Type 5）"""
        start_time = time.time()
        try:
            # 専用クラスでレスポンスをパース
            response = ReportResponse.from_bytes(data)

            # 専用クラスのメソッドでsource情報を取得
            source_info = response.get_source_info()
            if not source_info:
                print(
                    f"530: [{self.server_name}] 処理エラー: レポートレスポンスに送信元情報がありません"
                )
                if hasattr(response, "ex_field"):
                    self.logger.debug(
                        f"  ex_field の内容: {response.ex_field.to_dict()}"
                    )
                return

            # source情報の検証と正規化
            try:
                host, port = self._validate_source_info(source_info)
                dest_addr = (host, port)
            except Exception:
                print(f"[{self.server_name}] 不正なsource_info形式: {source_info}")
                return

            # source情報を変数に格納したので拡張フィールドから削除
            self._strip_source_from_ex_field(response)

            try:
                # レスポンスのバージョンを現在のサーバーバージョンで設定
                response.version = self.version  # バージョンを正規化
                final_data = response.to_bytes()

                # 元のクライアントに送信
                try:
                    self._sendto_and_check(final_data, dest_addr)

                    # 統一されたデバッグ出力を追加
                    execution_time = time.time() - start_time
                    debug_data = {
                        "area_code": (
                            response.area_code
                            if hasattr(response, "area_code")
                            else "N/A"
                        ),
                        "timestamp": response.timestamp,
                        "status": "success",
                        "response_type": "report_response",
                        "packet_id": response.packet_id,
                        "data_sent": len(final_data),
                    }
                    self.packet_debug_logger.log_unified_packet_received(
                        "Report response forwarding", execution_time, debug_data
                    )

                except Exception as e:
                    self.logger.debug(traceback.format_exc())
                    # ErrorResponseを作成して返す
                    self._send_error_to_dest(530, response.packet_id, dest_addr)
                    raise RuntimeError(
                        f"天気サーバーでの処理エラー: クライアントへの転送に失敗 {str(e)}"
                    )

            except Exception as conv_e:
                print(f"530: [{self.server_name}] 処理エラー: {conv_e}")
                self.logger.debug(traceback.format_exc())
                # ErrorResponseを作成して返す
                self._send_error_to_dest(530, response.packet_id, dest_addr)
                return

        except Exception as e:
            print(
                f"530: [{self.server_name}] レポートレスポンス処理中にエラーが発生しました: {e}"
            )
            self.logger.debug(traceback.format_exc())
            # ErrorResponseを作成して返す（responseが未定義の場合の処理を追加）
            packet_id = (
                getattr(response, "packet_id", 0) if "response" in locals() else 0
            )
            # dest_addrが未定義の場合はaddrを使用
            dest_addr = locals().get("dest_addr", addr)
            self._send_error_to_dest(530, packet_id, dest_addr)
            return

    def create_response(self, request):
        """
        レスポンスを作成（プロキシサーバーなので基本的に使用しない）

        Args:
            request: リクエストオブジェクト

        Returns:
            レスポンスのバイナリデータ
        """
        # エラーレスポンスなどが必要な場合に実装
        return b""

    def parse_request(self, data):
        """
        リクエストデータをパース（専用パケットクラス使用）

        Args:
            data: 受信したバイナリデータ

        Returns:
            専用パケットクラスのインスタンス
        """
        # まず基本的なパケットを解析してタイプを確認
        from WIPCommonPy.packet import Request

        temp_request = Request.from_bytes(data)
        packet_type = temp_request.type

        # タイプに応じて適切な専用クラスでパース
        if packet_type == 0:
            # 座標解決リクエスト
            return LocationRequest.from_bytes(data)
        elif packet_type == 1:
            # 座標解決レスポンス
            return LocationResponse.from_bytes(data)
        elif packet_type == 2:
            # 気象データリクエスト
            return QueryRequest.from_bytes(data)
        elif packet_type == 3:
            # 気象データレスポンス
            return QueryResponse.from_bytes(data)
        elif packet_type == 4:
            # データレポートリクエスト
            return ReportRequest.from_bytes(data)
        elif packet_type == 5:
            # データレポートレスポンス
            return ReportResponse.from_bytes(data)
        elif packet_type == 7:  # エラーパケット
            return ErrorResponse.from_bytes(data)
        else:
            # 不明なタイプの場合は基本クラスを返す
            return temp_request

    def validate_request(self, request):
        """
        リクエストの妥当性をチェック（改良版）

        Args:
            request: リクエストオブジェクト

        Returns:
            tuple: (is_valid, error_message)
        """
        if request.version != self.version:
            return (
                False,
                "403",
                f"バージョンが不正です (expected: {self.version}, got: {request.version})",
            )

        # タイプのチェック（0-3,4,5,7が有効）
        if request.type not in [0, 1, 2, 3, 4, 5, 7]:
            return False, "400", f"不正なパケットタイプ: {request.type}"

        # エリアコードのチェック (タイプ0と7は除外)
        if request.type not in [0, 7] and (
            not request.area_code or request.area_code == "000000"
        ):
            return False, "402", "エリアコードが未設定"

        # 専用クラスのバリデーションメソッドを使用
        if hasattr(request, "is_valid") and callable(getattr(request, "is_valid")):
            if not request.is_valid():
                return False, "400", "専用クラスのバリデーションに失敗"

        return True, None, None

    def _debug_print_request(self, data, parsed):
        """リクエストのデバッグ情報を出力（統一フォーマット）"""
        if not self.debug:
            return

        details = {
            "Packet ID": getattr(parsed, "packet_id", "N/A"),
            "Type": getattr(parsed, "type", "N/A"),
            "Area": getattr(parsed, "area_code", "N/A"),
        }
        if hasattr(parsed, "get_request_summary"):
            details["Summary"] = parsed.get_request_summary()

        log = UnifiedLogFormatter.format_communication_log(
            server_name=self.server_name,
            direction="recv from",
            remote_addr="unknown",
            remote_port=0,
            packet_size=len(data),
            packet_details=details,
        )
        self.logger.debug(log)

    def _cleanup(self):
        """派生クラス固有のクリーンアップ処理（オーバーライド）"""
        # クライアントのクリーンアップ
        if hasattr(self, "location_client"):
            self.location_client.close()
        if hasattr(self, "query_client"):
            self.query_client.close()
