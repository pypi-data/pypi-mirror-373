"""
警報・注意報情報取得スクリプト

リファクタリング済みのAlertProcessorを使用して
警報・注意報情報を取得・処理し、Redisに格納します。

使用方法:
    python get_alert.py
"""

import sys
import os
from pathlib import Path

# パスを追加して直接実行にも対応
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from WIPServerPy.data.alert_processor import AlertDataProcessor, AlertProcessor
from WIPServerPy.data.redis_manager import create_redis_manager

# JSON_DIR references removed


def main():
    """
    警報・注意報処理のメイン関数

    AlertProcessorを使用して警報・注意報情報を取得し、
    既存のRedis気象データに追加します。
    """
    print("=== 警報・注意報情報取得開始 ===")

    # AlertDataProcessorのインスタンスを作成
    processor = AlertDataProcessor()
    lister = AlertProcessor()
    try:
        # Step 1: XMLファイルリストの取得
        print("Step 1: Getting XML file list...")
        url_list = lister.get_alert_xml_list()

        print(f"Found {len(url_list)} URLs")
        if not url_list:
            print("No URLs found. Exiting.")
            return

        # Step 2: 警報・注意報情報の取得・統合
        print("Step 2: Processing alert info...")
        json_result = processor.get_alert_info(url_list)

        print("\n=== 警報・注意報情報取得完了===")

        # Redis管理クラスを使用してデータを更新
        print("\n=== Redisデータ更新開始 ===")

        try:
            # Redis管理クラスのインスタンスを作成
            redis_manager = create_redis_manager(debug=True)

            # 警報・注意報情報を更新
            # RedisManagerのupdate_alertsはarea_alert_mapping部分を期待
            result = redis_manager.update_alerts(json_result)

            # 結果を表示
            print(f"\n=== Redis更新結果 ===")
            print(f"更新されたエリア: {result['updated']}件")
            print(f"新規作成されたエリア: {result['created']}件")
            print(f"エラー: {result['errors']}件")
            print(f"合計処理エリア: {result['updated'] + result['created']}件")

            # 接続を閉じる
            redis_manager.close()

            print("=== Redisデータ更新完了 ===")

        except Exception as e:
            print(f"Redis更新エラー: {e}")
    except Exception as e:
        print(f"Error in alert processing: {e}")


