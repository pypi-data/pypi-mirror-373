# titanic-ml-pipeline

Pipeline de ML con scikit-learn usando el dataset Titanic (seaborn):
- Imputación numérica (mediana) + escalado
- Imputación categórica (constant='missing') + OneHot
- Reducción con TruncatedSVD
- Regresión logística

## Instalación local
```bash
pip install build
py -m build
pip install dist/titanic_ml_pipeline-0.1.0-py3-none-any.whl
