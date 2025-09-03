import os
import sys
from timeit import default_timer as timer
import pandas as pd
from loguru import logger
from .modules import *

class Claridata:

    def __init__(self, input_data, mode='auto', duplicates=False, missing_num=False, 
                 missing_categ=False, encode_categ=False, extract_datetime=False, 
                 outliers=False, outlier_param=1.5, logfile=True, verbose=False):  
        """
        Main class for automated data cleaning.
        """
        start = timer()
        self._initialize_logger(verbose, logfile)
        
        output_data = input_data.copy()

        if mode == 'auto':
            duplicates, missing_num, missing_categ, outliers, encode_categ, extract_datetime = 'auto', 'auto', 'auto', 'winz', ['auto'], 's'

        self.mode = mode
        self.duplicates = duplicates
        self.missing_num = missing_num
        self.missing_categ = missing_categ
        self.outliers = outliers
        self.encode_categ = encode_categ
        self.extract_datetime = extract_datetime
        self.outlier_param = outlier_param
        
        self._validate_params(output_data, verbose, logfile)
        
        self.output = self._clean_data(output_data, input_data)  

        end = timer()
        logger.info('Claridata process completed in {} seconds', round(end-start, 6))

        if not verbose:
            print('Claridata process completed in', round(end-start, 6), 'seconds')
        if logfile:
            
            print('Logfile saved to:', os.path.join(os.getcwd(), 'Claridata.log'))

    def _initialize_logger(self, verbose, logfile):
        logger.remove()
        if verbose:
            logger.add(sys.stderr, format='{time:DD-MM-YYYY HH:mm:ss.SS} - {level} - {message}')
        if logfile:    
            logger.add('datamolder.log', mode='w', format='{time:DD-MM-YYYY HH:mm:ss.SS} - {level} - {message}')

    def _validate_params(self, df, verbose, logfile):
        logger.info('Started validation of input parameters...')
        if type(df) != pd.DataFrame:
            raise ValueError('Invalid value for "input_data". Must be a pandas DataFrame.')
        if self.mode not in ['manual', 'auto']:
            raise ValueError('Invalid value for "mode".')
        if self.duplicates not in [False, 'auto']:
            raise ValueError('Invalid value for "duplicates".')
        if self.missing_num not in [False, 'auto', 'knn', 'mean', 'median', 'most_frequent', 'delete']:
            raise ValueError('Invalid value for "missing_num".')
        if self.missing_categ not in [False, 'auto', 'knn', 'most_frequent', 'delete']:
            raise ValueError('Invalid value for "missing_categ".')
        if self.outliers not in [False, 'auto', 'winz', 'delete']:
            raise ValueError('Invalid value for "outliers".')
        if isinstance(self.encode_categ, list):
            if len(self.encode_categ) > 2 or self.encode_categ[0] not in ['auto','onehot','label']:
                raise ValueError('Invalid value for "encode_categ".')
        else:
            if self.encode_categ not in ['auto', False]:
                raise ValueError('Invalid value for "encode_categ".')
        if not isinstance(self.outlier_param, (int, float)):
            raise ValueError('Invalid value for "outlier_param".')
        if self.extract_datetime not in [False,'auto','D','M','Y','h','m','s']:
            raise ValueError('Invalid value for "extract_datetime".')
        logger.info('Completed validation of input parameters.')

    def _clean_data(self, df, input_data):
        df = df.reset_index(drop=True)
        df = Duplicates.handle(self, df)
        df = MissingValues.handle(self, df)
        df = Outliers.handle(self, df)    
        df = Adjust.convert_datetime(self, df) 
        df = EncodeCateg.handle(self, df)     
        df = Adjust.round_values(self, df, input_data)
        return df
