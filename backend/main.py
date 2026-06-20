from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, func
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime, date, timedelta

SQLALCHEMY_DATABASE_URL = "sqlite:///./dulce_descontrol.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- MODELOS ---
class ClienteDB(Base):
    __tablename__ = "Clientes"
    id_cliente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    pedidos = relationship("PedidoDB", back_populates="cliente")

class IngredienteDB(Base):
    __tablename__ = "Ingredientes"
    id_ingrediente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    unidad_medida = Column(String, nullable=False)
    stock = Column(Float, default=0.0)

class PedidoIngredienteDB(Base):
    __tablename__ = "Pedido_Ingrediente"
    id_pedido = Column(Integer, ForeignKey("Pedidos.id_pedido", ondelete="CASCADE"), primary_key=True)
    id_ingrediente = Column(Integer, ForeignKey("Ingredientes.id_ingrediente", ondelete="CASCADE"), primary_key=True)
    cantidad_necesaria = Column(Float, nullable=False)

class PedidoDB(Base):
    __tablename__ = "Pedidos"
    id_pedido = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey("Clientes.id_cliente", ondelete="CASCADE"), nullable=False)
    fecha_pedido = Column(String, nullable=False)
    fecha_entrega = Column(String, nullable=False)
    estado = Column(String, nullable=False)
    monto_total = Column(Integer, default=0)
    detalles = Column(String, nullable=True)
    cliente = relationship("ClienteDB", back_populates="pedidos")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Dulce Descontrol")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- ESQUEMAS ---
class PedidoClienteNuevo(BaseModel):
    nombre_cliente: str
    email_cliente: str
    fecha_entrega: str
    producto: str
    requisitos: str
    monto_total: int

class EstadoUpdate(BaseModel):
    estado: str

# --- ENDPOINTS ---

@app.put("/pedidos/{id_pedido}/estado")
def actualizar_estado(id_pedido: int, estado_update: EstadoUpdate, db: Session = Depends(get_db)):
    pedido = db.query(PedidoDB).filter(PedidoDB.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    pedido.estado = estado_update.estado
    db.commit()
    return {"message": "Estado actualizado"}

@app.post("/pedidos/cliente", status_code=201)
def crear_pedido_desde_app(pedido: PedidoClienteNuevo, db: Session = Depends(get_db)):
    cliente = db.query(ClienteDB).filter(ClienteDB.email == pedido.email_cliente).first()
    if not cliente:
        cliente = ClienteDB(nombre=pedido.nombre_cliente, email=pedido.email_cliente)
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        
    nuevo_pedido = PedidoDB(
        id_cliente=cliente.id_cliente,
        fecha_pedido=date.today().strftime("%Y-%m-%d"),
        fecha_entrega=pedido.fecha_entrega,
        estado="Cotizado",
        monto_total=pedido.monto_total,
        detalles=f"{pedido.producto} | Notas: {pedido.requisitos}"
    )
    db.add(nuevo_pedido)
    db.flush() # Guardamos temporalmente para obtener el id_pedido

    # RECETARIO AUTOMÁTICO (ID_ingrediente, Cantidad)
    recetas = {
        "Torta de Chocolate": [(1, 1.0), (2, 1.0), (3, 5.0), (5, 0.5)], 
        "Pie de Limón": [(1, 0.5), (2, 0.8), (3, 4.0), (4, 0.2)],
        "Torta de Zanahoria": [(1, 1.2), (2, 1.0), (3, 4.0), (4, 0.3)],
        "Cheesecake de Frambuesa": [(2, 0.5), (3, 3.0), (6, 0.8), (7, 0.5)], # Usa queso crema y frambuesas
        "Torta Tres Leches": [(1, 1.0), (2, 1.0), (3, 6.0)],
        "Caja 12 Cupcakes": [(1, 0.5), (2, 0.5), (3, 2.0), (4, 0.2)]
    }

    if pedido.producto in recetas:
        for id_ing, cant in recetas[pedido.producto]:
            db.add(PedidoIngredienteDB(id_pedido=nuevo_pedido.id_pedido, id_ingrediente=id_ing, cantidad_necesaria=cant))
            
    db.commit()
    return {"message": "Pedido recibido"}

@app.get("/dashboard/resumen")
def obtener_resumen_dashboard(db: Session = Depends(get_db)):
    hoy_str = date.today().strftime("%Y-%m-%d")
    fin_semana_str = (date.today() + timedelta(days=(6 - date.today().weekday()))).strftime("%Y-%m-%d")
    
    pedidos_hoy = db.query(PedidoDB).filter(PedidoDB.fecha_entrega == hoy_str).count()
    pedidos_semana = db.query(PedidoDB).filter(PedidoDB.fecha_entrega >= hoy_str, PedidoDB.fecha_entrega <= fin_semana_str).count()
    ganancias_mes = db.query(func.sum(PedidoDB.monto_total)).filter(PedidoDB.estado.in_(["Confirmado", "En producción"])).scalar() or 0

    ingredientes_faltantes = []
    # SOLO SE COMPRAN INGREDIENTES PARA PEDIDOS CONFIRMADOS O EN PRODUCCIÓN
    pedidos_activos = db.query(PedidoDB.id_pedido).filter(PedidoDB.estado.in_(["Confirmado", "En producción"])).all()
    id_pedidos_activos = [p[0] for p in pedidos_activos]
    
    if id_pedidos_activos:
        requerimientos = db.query(
            PedidoIngredienteDB.id_ingrediente,
            func.sum(PedidoIngredienteDB.cantidad_necesaria).label("total")
        ).filter(PedidoIngredienteDB.id_pedido.in_(id_pedidos_activos)).group_by(PedidoIngredienteDB.id_ingrediente).all()
        
        for req in requerimientos:
            ing = db.query(IngredienteDB).filter(IngredienteDB.id_ingrediente == req.id_ingrediente).first()
            if ing and ing.stock < req.total:
                ingredientes_faltantes.append({"ingrediente": ing.nombre, "unidad": ing.unidad_medida, "falta": round(req.total - ing.stock, 2)})

    ultimos = db.query(PedidoDB).order_by(PedidoDB.id_pedido.desc()).limit(10).all()
    lista_pedidos = [{"id": p.id_pedido, "cliente": p.cliente.nombre, "fecha": p.fecha_entrega, "estado": p.estado, "detalles": p.detalles, "monto": p.monto_total} for p in ultimos]

    return {"entregas_hoy": pedidos_hoy, "entregas_semana": pedidos_semana, "ganancias_proyectadas_mes": ganancias_mes, "compras_necesarias": ingredientes_faltantes, "ultimos_pedidos": lista_pedidos}