from .models import SerieTemporal
import pandas as pd

def get_data_serie(posto_id):
    serie = {}
    postos = SerieTemporal.objects.filter(Id = posto_id)
    for posto in postos:
        serie[posto.data_e_hora] = posto.dados
    data_series = pd.Series(data=serie)
    return data_series