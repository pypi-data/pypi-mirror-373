import subprocess
import sys

class NkfConverter:
    def __init__(self, nkf_args=None):
        """
        コンストラクタ
        :param nkf_args: nkf に渡す引数のリスト（例: ['-w', '--overwrite']）
                         指定しない場合はデフォルト値を使用
        """
        if nkf_args is None:
            nkf_args = ['-w', '--overwrite']
        self.nkf_args = nkf_args

    def convert(self, file_path):
        """
        nkf を使ってファイルの文字コード変換を行う
        :param file_path: 変換対象のファイルパス
        :return: nkfの変換結果のバイト列、失敗したらNone
        """
        cmd = ['nkf32'] + self.nkf_args + [file_path]
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            print(f"nkfの実行完了しました: {file_path}")
        except subprocess.CalledProcessError as e:
            print(f"nkfの実行でエラーが発生しました: {e.stderr.decode()}", file=sys.stderr)
            return None
        return result.stdout