import re
import os
import logging

class CobolSplitter:
    def __init__(self, input_file):
        self.input_file = input_file
        self.identification_div = []
        self.environment_div = []
        self.data_div = []
        self.procedure_div = []  # list of tuples: (line_text, line_number)
        self.paragraphs = {}
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(message)s"
        )
        logging.debug(f"Initialized CobolSplitter for file: {input_file}")
    @staticmethod
    def normalize_whitespace(s):
        return re.sub(r'\s+', ' ', s).strip().upper()

    @classmethod
    def line_starts_with_division(cls, line, division_name):
        line_norm = cls.normalize_whitespace(line)
        division_norm = cls.normalize_whitespace(division_name)
        return line_norm.startswith(division_norm)

    def read_file(self):
        logging.debug(f"Reading file: {self.input_file}")
        with open(self.input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        div = None
        for idx, line in enumerate(lines, 1):  # 行番号は1始まり
            if self.line_starts_with_division(line, "IDENTIFICATION DIVISION"):
                div = "IDENTIFICATION"
                logging.debug(f"Found IDENTIFICATION DIVISION at line {idx}")
            elif self.line_starts_with_division(line, "ENVIRONMENT DIVISION"):
                div = "ENVIRONMENT"
                logging.debug(f"Found ENVIRONMENT DIVISION at line {idx}")
            elif self.line_starts_with_division(line, "DATA DIVISION"):
                div = "DATA"
                logging.debug(f"Found DATA DIVISION at line {idx}")
            elif self.line_starts_with_division(line, "PROCEDURE DIVISION"):
                div = "PROCEDURE"
                logging.debug(f"Found PROCEDURE DIVISION at line {idx}")
            elif line.strip() == ".":
                div = None
                logging.debug(f"Division end at line {idx}")

            if div == "IDENTIFICATION":
                self.identification_div.append(line)
            elif div == "ENVIRONMENT":
                self.environment_div.append(line)
            elif div == "DATA":
                self.data_div.append(line)
            elif div == "PROCEDURE":
                self.procedure_div.append( (line, idx) )  # タプルで行テキストと行番号を保持
            else:
                self.identification_div.append(line)
        logging.debug("Finished reading and splitting divisions.")

    def split_paragraphs(self):
        logging.debug("Splitting PROCEDURE DIVISION into paragraphs.")
        procedure_lines = self.procedure_div[:]
        if procedure_lines and self.line_starts_with_division(procedure_lines[0][0], "PROCEDURE DIVISION"):
            procedure_lines.pop(0)

        para_header_re = re.compile(r"^\s*([A-Z0-9\-]+)\.\s*$", re.I)

        current_para = None
        current_lines = []

        for line, lineno in procedure_lines:
            m = para_header_re.match(line)
            if m:
                if current_para:
                    self.paragraphs[current_para] = current_lines
                    logging.debug(f"Paragraph '{current_para}' ends at line {lineno}")
                current_para = m.group(1)
                current_lines = [(line, lineno)]
                logging.debug(f"Paragraph '{current_para}' starts at line {lineno}")
            else:
                if current_para:
                    current_lines.append((line, lineno))
                else:
                    current_para = "MAIN"
                    current_lines = [(line, lineno)]
        if current_para:
            self.paragraphs[current_para] = current_lines
            logging.debug(f"Paragraph '{current_para}' ends at last line.")
        logging.debug(f"Total paragraphs found: {len(self.paragraphs)}")

    def write_files(self):
        logging.debug("Writing split paragraphs to files.")
        created_files = []

        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        input_dir = os.path.dirname(self.input_file)
        outdir = os.path.join(input_dir, base_name)
        os.makedirs(outdir, exist_ok=True)
        logging.debug(f"Output directory created: {outdir}")

        for para, lines_para in self.paragraphs.items():
            # パラグラフの開始行番号を取得
            start_line = lines_para[0][1] if lines_para else 0
            outfname = os.path.join(outdir, f"{base_name}_{para}_{start_line}.cbl")

            with open(outfname, "w", encoding="utf-8") as f:
                # パラグラフの内容のみを出力（行番号コメントなし）
                for line, lineno in lines_para:
                    f.write(line)
                    if not line.endswith("\n"):
                        f.write("\n")

            created_files.append(outfname)
            logging.info(f"Created: {outfname}")

        logging.debug("All paragraph files written.")
        return created_files

    def run(self):
        logging.info("CobolSplitter run started.")
        self.read_file()
        self.split_paragraphs()
        created_files = self.write_files()
        logging.info("CobolSplitter run finished.")
        return created_files
