"""
レスポンスパケット（統合版）
"""

from typing import Optional, Dict, Any, Union
from pathlib import Path
from WIPCommonPy.packet.core.exceptions import BitFieldError
from WIPCommonPy.packet.core.format_base import FormatBase
from WIPCommonPy.packet.core.extended_field import ExtendedField
from WIPCommonPy.packet.core.bit_utils import extract_bits, extract_rest_bits
from WIPCommonPy.packet.dynamic_format import load_response_fields


_RESPONSE_SPEC: Dict[str, Dict[str, Any]] = load_response_fields()


def _apply_response_spec(spec: Dict[str, Dict[str, Any]]) -> None:
    """内部利用: レスポンスフィールド定義をクラスに適用"""
    old_fields = set(getattr(Response, "FIXED_FIELD_LENGTH", {}))
    fixed_length = {
        k: int(v.get("length", v))
        for k, v in spec.items()
        if k not in FormatBase.FIELD_LENGTH
    }

    Response.FIXED_FIELD_LENGTH = fixed_length
    Response.FIXED_FIELD_POSITION = {}
    current_pos = sum(FormatBase.FIELD_LENGTH.values())
    for field, length in fixed_length.items():
        Response.FIXED_FIELD_POSITION[field] = current_pos
        current_pos += length

    Response.VARIABLE_FIELD_START = current_pos

    ranges: Dict[str, tuple[int, int]] = {}
    for field, length in fixed_length.items():
        if field == "pop":
            ranges[field] = (0, 100)
        else:
            ranges[field] = (0, (1 << length) - 1)
    Response.FIXED_FIELD_RANGES = ranges

    removed = old_fields - set(fixed_length)
    for field in removed:
        if hasattr(Response, field):
            delattr(Response, field)

    # 新しいフィールドに合わせてプロパティを生成
    Response._generate_properties()


class Response(FormatBase):
    """
    レスポンスパケット

    基本フィールド:
    - 共通ヘッダー (Format クラスと同じ)

    固定長拡張フィールド:
    - weather_code (129-144bit, 16ビット):
        天気コード。0-65535の範囲で天気状態を表す。

    - temperature (145-152bit, 8ビット):
        気温。0-255の範囲で気温を表す。
        実際の気温は、この値から100を引いた値となる（-100℃～+155℃）。

    - pop (153-160bit, 8ビット):
        降水確率 (precipitation_prob)。
        0-100の範囲でパーセント値を表す。

    可変長拡張フィールド (161bit-):
    - ex_field: 可変長の拡張データ
        - alert: 警報情報 (文字列のリスト)
        - disaster: 災害情報 (文字列のリスト)
        - latitude: 緯度 (数値)
        - longitude: 経度 (数値)
        - source: 送信元情報 (ip, port) のタプル
    """

    @classmethod
    def _generate_properties(cls) -> None:
        """FIXED_FIELD_LENGTHに基づきプロパティを動的生成"""
        for field in cls.FIXED_FIELD_LENGTH:

            def getter(self, *, _f=field):
                return getattr(self, f"_{_f}", 0)

            def setter(self, value: int, *, _f=field) -> None:
                self._set_validated_extended_field(_f, value)

            setattr(cls, field, property(getter, setter))

    def get_coordinates(self) -> Optional[tuple[float, float]]:
        """
        拡張フィールドから緯度経度を取得する

        Returns:
            緯度経度のタプル (latitude, longitude)、存在しない場合はNone
        """
        ex_dict = self.ex_field.to_dict()
        if "latitude" in ex_dict and "longitude" in ex_dict:
            return (float(ex_dict["latitude"]), float(ex_dict["longitude"]))
        return None

    def get_min_packet_size(self) -> int:
        """
        レスポンスパケットの最小サイズを取得する

        Returns:
            最小パケットサイズ（バイト） - 基本フィールド + 固定長拡張フィールド
        """
        base_size = super().get_min_packet_size()
        fixed_bits = sum(self.FIXED_FIELD_LENGTH.values())
        return base_size + fixed_bits // 8

    def __init__(
        self,
        *,
        ex_field: Optional[Union[Dict[str, Any], ExtendedField]] = None,
        **kwargs,
    ) -> None:
        """レスポンスパケットの初期化

        Args:
            ex_field: 拡張フィールド（辞書またはExtendedFieldオブジェクト）
            **kwargs: 基本フィールドおよび固定長フィールドのパラメータ

        Raises:
            BitFieldError: フィールド値が不正な場合
        """
        try:
            # チェックサム自動計算フラグ
            self._auto_checksum = True

            # 可変長拡張フィールドの初期化
            if isinstance(ex_field, dict):
                self._ex_field = ExtendedField(ex_field)
            elif isinstance(ex_field, ExtendedField):
                self._ex_field = ex_field
            else:
                self._ex_field = ExtendedField()

            fixed_values: Dict[str, Any] = {}
            base_kwargs: Dict[str, Any] = {}
            for key, value in kwargs.items():
                if key in self.FIXED_FIELD_LENGTH:
                    fixed_values[key] = value
                else:
                    base_kwargs[key] = value

            # ビット列が提供された場合はそのまま親クラスに渡す
            if "bitstr" in kwargs:
                for field in self.FIXED_FIELD_LENGTH:
                    setattr(self, field, 0)
                super().__init__(**base_kwargs)
                return

            # 固定長フィールドを初期化
            for field in self.FIXED_FIELD_LENGTH:
                setattr(self, field, 0)

            # 親クラスの初期化
            super().__init__(**base_kwargs)

            # 固定長フィールドの値を設定
            for field, value in fixed_values.items():
                self._set_validated_extended_field(field, value)

            # 拡張フィールドの変更を監視してチェックサムを再計算
            self._ex_field.add_observer(self._on_ex_field_changed)

        except BitFieldError:
            raise
        except Exception as e:
            raise BitFieldError("レスポンスパケットの初期化中にエラー: {}".format(e))

    def _on_ex_field_changed(self) -> None:
        """拡張フィールドが変更されたときの処理"""
        if (
            hasattr(self, "_auto_checksum")
            and self._auto_checksum
            and not getattr(self, "_in_from_bits", False)
        ):
            self._recalculate_checksum()

    @property
    def ex_field(self) -> ExtendedField:
        """拡張フィールドのプロパティ"""
        return self._ex_field

    @ex_field.setter
    def ex_field(self, value: Union[Dict[str, Any], ExtendedField]) -> None:
        """拡張フィールドの設定"""
        # 既存のオブザーバーを削除
        self._ex_field.remove_observer(self._on_ex_field_changed)

        # 新しい拡張フィールドを設定
        if isinstance(value, dict):
            self._ex_field = ExtendedField(value)
        elif isinstance(value, ExtendedField):
            self._ex_field = value
        else:
            self._ex_field = ExtendedField()

        # 新しいオブザーバーを追加
        self._ex_field.add_observer(self._on_ex_field_changed)

        # チェックサムを再計算（from_bits処理中でない場合）
        if not getattr(self, "_in_from_bits", False):
            self._on_ex_field_changed()

    def _set_validated_extended_field(self, field: str, value: int) -> None:
        """
        拡張フィールド値を検証して設定する

        Args:
            field: 設定するフィールド名
            value: 設定する値

        Raises:
            BitFieldError: 値が有効範囲外の場合
        """
        if field in self.FIXED_FIELD_RANGES:
            min_val, max_val = self.FIXED_FIELD_RANGES[field]
            if not (min_val <= value <= max_val):
                raise BitFieldError(
                    "フィールド '{}' の値 {} が有効範囲 {}～{} 外です".format(
                        field, value, min_val, max_val
                    )
                )

        # プロパティを避けて内部属性に直接設定
        object.__setattr__(self, f"_{field}", value)

    def from_bits(self, bitstr: int) -> None:
        """
        ビット列からフィールドを設定する

        Args:
            bitstr: 解析するビット列

        Raises:
            BitFieldError: ビット列の解析中にエラーが発生した場合
        """
        try:
            # from_bits処理中フラグを設定
            self._in_from_bits = True
            # 親クラスのフィールドを設定
            super().from_bits(bitstr)

            # 固定長拡張フィールドを設定（直接設定してチェックサム再計算を避ける）
            for field, pos in self.FIXED_FIELD_POSITION.items():
                length = self.FIXED_FIELD_LENGTH[field]
                value = extract_bits(bitstr, pos, length)
                # 値をマスクして有効範囲内に収める
                if field == "pop":
                    value &= 0xFF  # 8ビットマスク (0-255)
                elif field == "temperature":
                    value &= 0xFF  # 8ビットマスク (0-255)
                elif field == "weather_code":
                    value &= 0xFFFF  # 16ビットマスク (0-65535)
                # 直接設定（チェックサム再計算を避ける）
                object.__setattr__(self, field, value)

            # ex_flagが設定されていれば可変長拡張フィールドを解析
            if self.ex_flag == 1:
                ex_field_bits = extract_rest_bits(bitstr, self.VARIABLE_FIELD_START)
                if ex_field_bits:
                    # 総ビット長を計算（_total_bitsが設定されていれば使用）
                    ex_field_total_bits = getattr(self, "_total_bits", None)
                    if ex_field_total_bits:
                        ex_field_total_bits = (
                            ex_field_total_bits - self.VARIABLE_FIELD_START
                        )
                        self._ex_field = ExtendedField.from_bits(
                            ex_field_bits, ex_field_total_bits
                        )
                    else:
                        # _total_bitsが設定されていない場合はビット長から推定
                        self._ex_field = ExtendedField.from_bits(ex_field_bits)

                    # オブザーバーを追加
                    self._ex_field.add_observer(self._on_ex_field_changed)

        except BitFieldError:
            raise
        except Exception as e:
            raise BitFieldError("ビット列の解析中にエラー: {}".format(e))
        finally:
            # from_bits処理中フラグをクリア
            self._in_from_bits = False

    def to_bits(self) -> int:
        """
        全フィールドをビット列に変換する

        Returns:
            ビット列表現

        Raises:
            BitFieldError: ビット列への変換中にエラーが発生した場合
        """
        try:
            # 親クラスのビット列を取得
            bitstr = super().to_bits()

            # 固定長拡張フィールドを設定
            for field, pos in self.FIXED_FIELD_POSITION.items():
                length = self.FIXED_FIELD_LENGTH[field]
                value = getattr(self, field)
                # 値の検証は_set_validated_extended_fieldで行われているため、
                # ここでは単純にビット操作のみを行う
                bitstr |= (value & ((1 << length) - 1)) << pos

            # ex_fieldを設定（ExtendedFieldオブジェクトのto_bitsメソッドを使用）
            if self.ex_flag == 1 and self._ex_field and self._ex_field.to_dict():
                ex_field_bits = self._ex_field.to_bits()
                bitstr |= ex_field_bits << self.VARIABLE_FIELD_START

            return bitstr

        except BitFieldError:
            raise
        except Exception as e:
            raise BitFieldError("拡張ビット列への変換中にエラー: {}".format(e))

    def to_bytes(self) -> bytes:
        """
        ビット列をバイト列に変換する

        基本フィールドと拡張フィールドを含むすべてのデータをバイト列に変換します。
        チェックサムを計算して格納します。
        親クラスのメソッドを使用して最適なパディングを行います。

        Returns:
            バイト列表現

        Raises:
            BitFieldError: バイト列への変換中にエラーが発生した場合
        """
        # 親クラスの最適化されたto_bytes()を使用
        # get_min_packet_size()でレスポンスパケットの最小サイズ（20バイト）が設定される
        return super().to_bytes()

    def as_dict(self) -> Dict[str, Any]:
        """
        全フィールドを辞書形式で返す

        Returns:
            フィールド名と値の辞書
        """
        result = super().as_dict()
        # 固定長拡張フィールドを追加
        for field in self.FIXED_FIELD_LENGTH:
            result[field] = getattr(self, field)
        # 可変長拡張フィールドを追加（ExtendedFieldオブジェクトを辞書形式で）
        result["ex_field"] = self._ex_field.to_dict()
        return result


_apply_response_spec(_RESPONSE_SPEC)


def reload_response_spec(file_name: str | Path = "response_fields.json") -> None:
    """レスポンスフィールド定義を再読み込みする"""
    spec = load_response_fields(file_name)
    _apply_response_spec(spec)
