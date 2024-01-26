import numpy as np
import pandas as pd


class DataProcessEVP:
    def __init__(self, file_path=None, raw_data=None):
        _titulo = ''
        if raw_data is not None:
            _titulo, self._data = self.read_raw_data(raw_data)
        elif file_path is not None:
            _titulo, self._data = self.read_file(file_path)
        else:
            raise SyntaxError('File path or raw data must be passed as parameter.')

        self._data = self.data_to_np(self._data)
        self._data = self.np_to_dataframe(self._data, _titulo)

    @staticmethod
    def read_file(filename):
        data = []
        with open(filename) as file:
            titulo = file.readline().split()
            for f in file:
                data.append(f.split())

        titulo.pop(0)
        titulo.pop()
        titulo.pop()
        return titulo, data

    @staticmethod
    def read_raw_data(raw_data):
        data = []
        titulo = raw_data.readline().split()
        for f in raw_data:
            data.append(f.split())

        titulo.pop(0)
        titulo.pop()
        titulo.pop()

        return titulo, data

    @staticmethod
    def data_to_np(data, incorret_str='************'):
        # convert data list to numeric float data and convert incorrect
        # string (nonsignificant data) to NaN
        np_data = np.array(data)
        np_data = np.char.replace(np_data, incorret_str, 'NaN')
        np_data = np.array(np_data, dtype=float)
        return np_data

    @staticmethod
    def np_to_dataframe(data, cols_names):
        return pd.DataFrame(data=data, columns=cols_names)

    @property
    def data(self):
        return self._data


# if __name__ == '__main__':
#     dir_path = 'output_files_CPMD/'
#     file_path = dir_path + 'prefix.evp'
#     obj = DataProcessEVP(file_path)
#     # obj.data.info()
#     #print(obj.data['nfi'].tolist())
#     # print(obj.data[obj.data.nfi == obj.data['nfi'].tolist()])
#     import plotly.express as px
#
#     fig = px.line(obj.data.iloc[[2000.0, 2001.0, 2002.0],:], x='nfi', y='etot')
#     fig.show()
