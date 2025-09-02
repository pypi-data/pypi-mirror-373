# PrediPy

PrediPy adalah library Python ringan untuk **prediksi & regresi**. Mendukung:

- Linear Regression  
- Logistic Regression  
- Mini MLP (1 hidden layer)  
- Vectorized NumPy (paralel otomatis)  

## Instalasi

Setelah upload ke PyPI, bisa langsung install:

```bash
pip install predipy
# example 
from predipy import LinearRegression, LogisticRegression, MLP, mse, accuracy

# ===== Linear Regression =====
X = [[1],[2],[3]]
y = [2,4,6]
lr = LinearRegression()
lr.fit(X, y)
print("Linear Regression Predict:", lr.predict([[4]]))

# ===== Logistic Regression =====
X_cls = [[0],[1],[2],[3],[4]]
y_cls = [0,0,0,1,1]
log_model = LogisticRegression(lr=0.1, epochs=1000)
log_model.fit(X_cls, y_cls)
print("Logistic Regression Predict:", log_model.predict([[1],[2],[3]]))

# ===== MLP (Regression) =====
X_mlp = [[0],[1],[2],[3],[4],[5]]
y_mlp = [[0],[2],[4],[6],[8],[10]]
mlp_model = MLP(input_size=1, hidden_size=5, output_size=1, lr=0.01, epochs=2000)
mlp_model.fit(X_mlp, y_mlp)
print("MLP Predict:", mlp_model.predict([[6],[7]]))

