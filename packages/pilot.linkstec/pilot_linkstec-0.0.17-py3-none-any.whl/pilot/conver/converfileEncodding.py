import subprocess
import sys
import os

def nkf_convert(file_path, nkf_args):
    """
    nkf を使ってファイルの文字コード変換を行う

    :param file_path: 変換対象のファイルパス
    :param nkf_args: nkf に渡す引数のリスト（例: ['-w']）
    """
    # nkfコマンドの引数にファイルパスを追加
    #cmd = ['nkf'] + nkf_args + [file_path]

    cmd = ['nkf32'] + nkf_args + file_path


    try:
        # nkfを実行し標準出力を取得
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"nkfの実行完了しました: {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"nkfの実行でエラーが発生しました: {e.stderr.decode()}", file=sys.stderr)
        return None

    # nkfの変換結果（バイト列）を返す
    return result.stdout


#if __name__ == "__main__":
    # 処理対象のルートフォルダパスを指定（適宜変更してください）
#    root_folder = r"d:\work2\src"
#    nkf_convert(root_folder, ['-v'])



#if __name__ == "__main__":
#   if len(sys.argv) < 3:
    #        print(f"使い方: python {sys.argv[0]} <ファイルパス> <nkf引数...>", file=sys.stderr)
    #    print(f"例: python {sys.argv[0]} test.txt -w --overwrite", file=sys.stderr)
    #    sys.exit(1)

#    file_path = [r"D:\test\CHKCONST.cpy"]
#    nkf_args = ['-w','--overwrite']
    #nkf_args = ['-g']
#    output = nkf_convert(file_path, nkf_args)


if __name__ == "__main__":


    target_dir = r'D:\work\fullsource'
    nkf_args = ['-w', '--overwrite']
    #extensions = (
    #    '.cfc', '.cfm', '.cob', '.cobol', '.cpy', '.csh', '.css', '.ctl',
    #    '.htm', '.html', '.js', '.sh', '.sql', '.tpl', '.txt'
    #)
    extensions = ('.cnd','.cng','int')
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(extensions):
                filepath = os.path.join(root, file)
                output = nkf_convert([filepath], nkf_args)


    #if output is not None:
        # 結果を標準出力にバイナリのまま書き出す場合
        # sys.stdout.buffer.write(output)

        # あるいはUTF-8等に応じてデコードして表示する場合
        # 一旦utf-8デコードを試みる例（必要に応じて変更してください）
    #    try:
    #        decoded_output = output.decode('utf-8')
    #        print(decoded_output)
    #    except UnicodeDecodeError:
    #        print("utf-8へのデコードに失敗しました。バイナリデータとして出力します。", file=sys.stderr)
#        sys.stdout.buffer.write(output)