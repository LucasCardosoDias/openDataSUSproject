# -*- coding: utf-8 -*-

from sqlalchemy import types

def repository_items(item):

    r =    {'list_columns': ['_source.paciente_id', 
                             '_source.paciente_idade',
                             '_source.paciente_enumSexoBiologico',
                             '_source.paciente_racaCor_valor',
                             '_source.paciente_endereco_uf',
                             '_source.vacina_descricao_dose',
                             '_source.vacina_grupoAtendimento_nome',
                             '_source.vacina_categoria_nome',
                             '_source.vacina_fabricante_nome',
                             '_source.vacina_dataAplicacao'],
            'replace_dict': {'_source.paciente_id': 'paciente_id', 
                             '_source.paciente_idade': 'paciente_idade',
                             '_source.paciente_enumSexoBiologico': 'paciente_enumSexoBiologico',
                             '_source.paciente_racaCor_valor': 'paciente_racaCor_valor',
                             '_source.paciente_endereco_uf': 'paciente_endereco_uf',
                             '_source.vacina_descricao_dose': 'vacina_descricao_dose',
                             '_source.vacina_grupoAtendimento_nome': 'vacina_grupoAtendimento_nome',
                             '_source.vacina_categoria_nome': 'vacina_categoria_nome',
                             '_source.vacina_fabricante_nome': 'vacina_fabricante_nome',
                             '_source.vacina_dataAplicacao': 'vacina_dataAplicacao'},     
            'colunas':      ['paciente_id', 
                             'paciente_idade',
                             'paciente_enumSexoBiologico',
                             'paciente_racaCor_valor',
                             'paciente_endereco_uf',
                             'vacina_descricao_dose',
                             'vacina_grupoAtendimento_nome',
                             'vacina_categoria_nome',
                             'vacina_fabricante_nome',
                             'vacina_dataAplicacao'],
            
            'dtype':        {'paciente_id': types.TEXT, 
                             'paciente_idade': types.INT,
                             'paciente_enumSexoBiologico': types.TEXT,
                             'paciente_racaCor_valor': types.TEXT,
                             'paciente_endereco_uf': types.TEXT,
                             'vacina_descricao_dose': types.TEXT,
                             'vacina_grupoAtendimento_nome': types.TEXT,
                             'vacina_categoria_nome': types.TEXT,
                             'vacina_fabricante_nome': types.TEXT,
                             'vacina_dataAplicacao': types.TIMESTAMP}}   
    return r[item]

