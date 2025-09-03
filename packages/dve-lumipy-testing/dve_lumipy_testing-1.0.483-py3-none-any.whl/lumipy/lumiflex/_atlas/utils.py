import re

from pandas import DataFrame

from lumipy.lumiflex._common.str_utils import to_snake_case


def process_direct_provider_metadata(df: DataFrame) -> DataFrame:
    def extract_param_table(x):
        if isinstance(x, str):
            return '\n'.join(line for line in x.split('\n') if '│' in line)
        return ''

    def extract_description(x):
        descr = x.CustomSyntax.split(x.ParamTable)[0]
        descr = '\n'.join(descr.split('\n')[:-2])
        return descr.split('<OPTIONS>:')[0]

    def extract_body_str_names(x):
        use_chunks = x.split('enduse;')[0].split('use')[-1].replace('\n', '').split('----')
        use_chunks = [s for s in use_chunks if 'OPTIONS' not in s]
        use_chunks = [re.sub(r'[^A-Za-z0-9 ]+', '', s).strip() for s in use_chunks]
        use_chunks = [to_snake_case(s.replace(' ', '_')) for s in use_chunks if s != '']
        return use_chunks

    df['ParamTable'] = df.CustomSyntax.apply(extract_param_table)
    df = df[df.ParamTable != ''].copy()
    df['SyntaxDescr'] = df.apply(extract_description, axis=1)
    df['BodyStrNames'] = df.SyntaxDescr.apply(extract_body_str_names)

    return df.fillna('Not available')


def process_data_provider_metadata(df: DataFrame) -> DataFrame:
    df['IsMain'] = df.IsMain.astype(bool)
    df['IsPrimaryKey'] = df.IsPrimaryKey.astype(bool)
    return df.fillna('Not available')
