import os
import shutil

from pilot.job.job_interface import JobInterface
from pilot.logging.logger import get_logger


class BaseJob(JobInterface):
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config_dto = None
        self._current_step = None
        self._file_path = None
        self._step_index = None
        self._next_step = None
        self._next_step_file_path = None
        self._content = None


    @property
    def current_step(self):
        return self._current_step

    @current_step.setter
    def current_step(self, value):
        self._current_step = value

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value
        self._content = None  # ファイルパスが変わったらキャッシュクリア

    @property
    def step_index(self):
        return self._step_index

    @step_index.setter
    def step_index(self, value):
        self._step_index = value
        self._next_step = None  # step_indexが変わったらnext_stepをリセット

    @property
    def next_step(self):
        if self._next_step is None and self._step_index is not None:
            steps_list = self.config_dto.steps
            if self._step_index + 1 < len(steps_list):
                self._next_step = steps_list[self._step_index + 1]
            else:
                self._next_step = None
        return self._next_step

    @next_step.setter
    def next_step(self, value):
        self._next_step = value


    @property
    def current_trg_file_path(self):
        return self._trg_file_path

    @current_trg_file_path.setter
    def current_trg_file_path(self, value):
        self._trg_file_path = value




    def run(self):
        pass

    def get_file_content(self):
        if self._content is None and self._file_path:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                self._content = f.read()
        return self._content

    def get_current_step_relative_path(self):
        if not self._file_path:
            return self._file_path

        try:
            base_dir = os.path.join(self.config_dto.work_space, self.current_step)
            return os.path.relpath(self._file_path, base_dir)
        except ValueError:
            return self._file_path

    def get_current_step_count(self):
        if not self._file_path:
            return self.config_dto.work_space
        try:
            relative_path = self.get_current_step_relative_path()
            return os.path.relpath(self.config_dto.work_space, relative_path)
        except ValueError:
            return self.config_dto.work_space

    def _copy_file_to_step_dir(self, src_path, base_dir, step_dir):
        """指定したsrc_pathをbase_dirからの相対パスをごとstep_dir配下にコピーする。
           すでにコピー先に同名ファイルがあればNoneを返し、存在しなければコピー先ファイルパスを返す。
        """
        if not src_path:
            return None

        rel_path = os.path.relpath(os.path.dirname(src_path), base_dir)
        dest_dir = os.path.join(step_dir, rel_path)
        base_file_name = os.path.basename(src_path)
        dest_file_path = os.path.join(dest_dir, base_file_name)

        if os.path.exists(dest_file_path):
            self._next_step_file_path = dest_file_path
            return None

        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy(src_path, dest_file_path)
        self._next_step_file_path = dest_file_path
        return dest_file_path


    def copy_current_file_to_next_step(self):
        if not self._file_path or not self.next_step:
            return None
        base_dir = os.path.join(self.config_dto.work_space, self.current_step)
        step_dir = os.path.join(self.config_dto.work_space, self.next_step)
        return self._copy_file_to_step_dir(self._file_path, base_dir, step_dir)


    # 共通化メソッド
    def _create_next_step_trigger_file(self, ext):
        if self._next_step_file_path:
            trg_file = self._next_step_file_path + ".trg"
            end_file = self._next_step_file_path + ".end"
            begin_file = self._next_step_file_path + ".begin"
            target_file = self._next_step_file_path + ext
            if not (os.path.exists(trg_file) or os.path.exists(end_file) or os.path.exists(begin_file)):
                open(target_file, 'w', encoding='utf-8').close()
            return trg_file
        return None

    def create_next_step_todo_trg_file(self):
        return self._create_next_step_trigger_file(".trg")

    def create_next_step_end_trg_file(self):
        return self._create_next_step_trigger_file(".end")

    def create_next_step_begin_trg_file(self):
        return self._create_next_step_trigger_file(".begin")


    def change_current_trg_to_end(self):
        if os.path.exists(self.current_trg_file_path):
            file_path, file_extension = os.path.splitext(self.current_trg_file_path)
            if file_extension == ".trg" or file_extension == ".begin":
                try:
                    os.rename(self.current_trg_file_path, file_path + ".end")
                    return True
                except Exception:
                    # 例外が発生した場合は False を返す
                    print("!!!!!!!!!!!!!!!!!!!!change_current_trg_to_end erro")
                    return False
        # trgファイルが存在しなければ何もしないので、そのままreturn
        return False

    def change_current_trg_to_begin(self):
        if os.path.exists(self.current_trg_file_path):
            file_path, file_extension = os.path.splitext(self.current_trg_file_path)
            if file_extension == ".trg":
                try:
                    os.rename(self.current_trg_file_path, file_path + ".begin")
                    self.current_trg_file_path = os.path.join(file_path + ".begin")
                    return True
                except Exception:
                    # 例外が発生した場合は False を返す
                    return False
        return False

    def copy_input_file_to_next_step(self, input_file_path):
            """
            input_file_pathで指定されたファイルを、next stepフォルダにコピーする。
            コピー先に同名ファイルがあればNone、存在しなければコピー先ファイルパスを返す。
            """
            if not input_file_path or not self.next_step:
                return None
            base_dir = os.path.join(self.config_dto.work_space, self.current_step)
            step_dir = os.path.join(self.config_dto.work_space, self.next_step)
            return self._copy_file_to_step_dir(input_file_path, base_dir, step_dir)

    def create_next_step_todo_trg_file_from_input(self, input_file_path):
        """
        input_file_pathで指定されたファイルをnext stepフォルダにコピーし、.trgファイルを生成する。
        ファイルが既に存在する場合でも.trgファイルの作成を試行する。
        """
        if not input_file_path or not self.next_step:
            return None

        # ファイルをコピー（既存の場合はNoneが返される）
        copied_file_path = self.copy_input_file_to_next_step(input_file_path)

        # コピーが成功しなかった場合でも、対象ファイルパスを取得
        if not copied_file_path:
            base_dir = os.path.join(self.config_dto.work_space, self.current_step)
            step_dir = os.path.join(self.config_dto.work_space, self.next_step)
            rel_path = os.path.relpath(os.path.dirname(input_file_path), base_dir)
            dest_dir = os.path.join(step_dir, rel_path)
            base_file_name = os.path.basename(input_file_path)
            copied_file_path = os.path.join(dest_dir, base_file_name)

        # .trgファイルを作成
        trg_file = copied_file_path + ".trg"
        end_file = copied_file_path + ".end"
        begin_file = copied_file_path + ".begin"

        if not (os.path.exists(trg_file) or os.path.exists(end_file) or os.path.exists(begin_file)):
            # 空ファイルとして.trgファイルを生成
            open(trg_file, 'w', encoding='utf-8').close()
            return trg_file

        return None

    def create_current_step_end_trg_file_from_input(self, input_file_path):
        """
        input_file_pathで指定されたファイルに対して.endファイルを生成する。
        """
        if not input_file_path:
            return None

        trg_file = input_file_path + ".trg"
        end_file = input_file_path + ".end"
        begin_file = input_file_path + ".begin"

        # マーカーファイルが存在しない場合のみ.endファイルを作成
        if not (os.path.exists(trg_file) or os.path.exists(end_file) or os.path.exists(begin_file)):
            # 空ファイルとして.endファイルを生成
            open(end_file, 'w', encoding='utf-8').close()
            return end_file
        return None


    def create_trg_file_in_file_path_dir(self, file_name):
        """
        file_pathのディレクトリ配下に指定されたファイル名の.trgファイルを作成する。
        既に.trg, .end, .beginファイルが存在する場合は何もしない。
        """
        if not self._file_path or not file_name:
            return None
        dir_path = os.path.dirname(self._file_path)
        base_path = os.path.join(dir_path, file_name)
        trg_file = base_path + ".trg"
        end_file = base_path + ".end"
        begin_file = base_path + ".begin"
        if not (os.path.exists(trg_file) or os.path.exists(end_file) or os.path.exists(begin_file)):
            # 空ファイルとして.trgファイルを生成
            open(trg_file, 'w', encoding='utf-8').close()
            return trg_file
        return None

    def get_work_space(self):
        """
        config_dtoからwork_spaceを取得するメソッド
        """
        return self.config_dto.work_space

    def copy_file_and_todo_trg_to_next_step(self, result_file):
        self.create_current_step_end_trg_file_from_input(result_file)
        next_step_file = self.copy_input_file_to_next_step(result_file)
        self.create_next_step_todo_trg_file_from_input(next_step_file)


    def copy_file_and_end_trg_to_next_step(self, result_file):
        self.create_current_step_end_trg_file_from_input(result_file)
        next_step_file = self.copy_input_file_to_next_step(result_file)
        self.create_next_step_end_trg_file_from_input(next_step_file)

    def change_trg_file_to_end_in_file(self, file_name):
        """
        file_pathのディレクトリ配下に指定されたファイル名の.trgまたは.beginファイルが存在すれば、.endにリネームする。
        成功時 True、失敗時 False を返す。
        """
        if not self._file_path or not file_name:
            return False
        dir_path = os.path.dirname(self._file_path)
        base_path = os.path.join(dir_path, file_name)
        trg_file = base_path + ".trg"
        begin_file = base_path + ".begin"
        end_file = base_path + ".end"
        # .trgまたは.beginが存在すれば.endにリネーム
        if os.path.exists(begin_file):
            try:
                os.rename(trg_file, end_file)
                return True
            except Exception:
                print(f"change_trg_file_to_end_in_file error: {trg_file}")
                return False
        return False



    def create_next_step_end_trg_file_from_input(self, input_file_path):
        """
        input_file_pathで指定されたファイルをnext stepフォルダにコピーし、.trgファイルを生成する。
        ファイルが既に存在する場合でも.trgファイルの作成を試行する。
        """
        if not input_file_path or not self.next_step:
            return None

        # ファイルをコピー（既存の場合はNoneが返される）
        copied_file_path = self.copy_input_file_to_next_step(input_file_path)

        # コピーが成功しなかった場合でも、対象ファイルパスを取得
        if not copied_file_path:
            base_dir = os.path.join(self.config_dto.work_space, self.current_step)
            step_dir = os.path.join(self.config_dto.work_space, self.next_step)
            rel_path = os.path.relpath(os.path.dirname(input_file_path), base_dir)
            dest_dir = os.path.join(step_dir, rel_path)
            base_file_name = os.path.basename(input_file_path)
            copied_file_path = os.path.join(dest_dir, base_file_name)

        # .trgファイルを作成
        trg_file = copied_file_path + ".trg"
        end_file = copied_file_path + ".end"
        begin_file = copied_file_path + ".begin"

        if not (os.path.exists(trg_file) or os.path.exists(end_file) or os.path.exists(begin_file)):
            # 空ファイルとして.trgファイルを生成
            open(end_file, 'w', encoding='utf-8').close()
            return end_file

        return None

    def pre_run(self):
        """
        ジョブ実行前の前処理を行うメソッド。
        必要に応じてサブクラスでオーバーライドして使用する。
        """
        pass

    def post_run(self):
        """
        ジョブ実行後の後処理を行うメソッド。
        必要に応じてサブクラスでオーバーライドして使用する。
        """
        pass


