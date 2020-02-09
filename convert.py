import os


class Convert:
    source = []

    data = []

    def __init__(self, source, folder=""):
        sources = []
        folder = folder.rstrip("/")
        default_source_file = folder + "/" + source.lstrip("/") if folder != "" else source
        if os.path.exists(default_source_file):
            sources.append(default_source_file)
        elif "," in source:
            if folder != "":
                sources = [folder + "/" + r.lstrip("/") for r in source.split(",") if os.path.exists(folder + "/" + r.lstrip("/"))]
            else:
                sources = [r for r in source.split(",") if os.path.exists(r)]
        if len(sources) == 0:
            raise Exception("Unable to load the specified file: %s" % default_source_file)

        self.source = sources

    def __str__(self):
        msg = ""
        for row in self.data:
            msg += row['source'] + " -> " + row['dest'] + "\t" + (
                "OK" if row['read'] and row['write'] else "Failed") + "\r\n"
        return msg

    def read(self):
        for f in self.source:
            t = {
                "source": f,
                "data": [],
                "suffix": os.path.splitext(f)[1].lower(),
                "read": False,
                "write": False,
                "dest": "",
            }
            if t["suffix"] == ".csv":
                from reader.csv import CsvReader
                cr = CsvReader(f)
                t["data"] = cr.load()
                if len(t["data"]) > 0:
                    t["read"] = True
            else:
                continue
            self.data.append(t)
        return self

    def write(self, **kwargs):
        convert_file_type = "xlsx"
        if "type" in kwargs:
            convert_file_type = kwargs['type']
        merge = 0
        if "merge" in kwargs:
            merge = kwargs['merge']
        filename = ""
        if "dest" in kwargs and kwargs['dest'] != '':
            filename = kwargs['dest']
        if convert_file_type == "xlsx":
            self._write_to_excel(merge, filename)
        else:
            raise Exception("Unsupport Convert Type.")
        return self

    def _write_to_excel(self, merge, dest_filename):
        from writer.xlsx import XlsxWriter
        if merge == 1:  # 合并数据到一个工作表中
            filename = ''
            data = []
            for row in self.data:
                if not row['read']:
                    continue
                if filename == "":
                    filename = row['source'] + ".m"
                data.extend(row['data'])
            if dest_filename != "":
                filename = dest_filename
            xw = XlsxWriter(filename)
            xw.write(data)
            for row in self.data:
                if not row['read']:
                    continue
                row['write'] = True
                row['dest'] = xw.filename
        elif merge == 2:  # 合并到一个文件的多个工作表中
            filename = ''
            data = []
            for row in self.data:
                if not row['read']:
                    continue
                if filename == "":
                    filename = row['source'] + ".s"
                data.append({
                    "title": os.path.basename(row['source']).lower(),
                    "data": row['data']
                })
            if dest_filename != "":
                filename = dest_filename
            xw = XlsxWriter(filename)  
            xw.write_multi(data)
            for row in self.data:
                if not row['read']:
                    continue
                row['write'] = True
                row['dest'] = xw.filename
        else:  # 不合并，导出为多个文件
            cnt = len(self.data)
            for row in self.data:
                if not row['read']:
                    continue
                if cnt == 1 and dest_filename != "":
                    xw = XlsxWriter(dest_filename)
                else:
                    xw = XlsxWriter(row['source'])
                xw.write(row['data'])
                row['write'] = True
                row['dest'] = xw.filename

        return self
