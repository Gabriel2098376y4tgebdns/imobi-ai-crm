from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from core.config import get_settings
from core.logger import logger, setup_logging

# Configurar settings
settings = get_settings()

# Reconfigurar logs com settings
setup_logging(settings.log_level, settings.log_file)

app = FastAPI(
    title="Imobi AI CRM",
    description="Sistema de Follow-up Inteligente para Imobiliárias",
    version="0.1.0"
)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Imobi AI CRM iniciando...")
    logger.info(f"Ambiente: {settings.environment}")
    logger.info(f"Database: {settings.database_url}")
    logger.info(f"Redis: {settings.redis_url}")

@app.get("/")
def read_root():
    logger.info("Endpoint raiz acessado")
    return {
        "message": "Imobi AI CRM funcionando!",
        "status": "online",
        "estrutura": "AI RECOMENDACAO/imobi-ai-crm",
        "environment": settings.environment
    }

@app.get("/health")
def health_check():
    logger.info("Health check realizado")
    return {
        "status": "healthy", 
        "service": "imobi-ai-crm",
        "environment": settings.environment,
        "database": settings.database_url,
        "redis": settings.redis_url
    }

@app.get("/xml-exemplo")
def get_xml_exemplo():
    """Retornar URL do XML de exemplo local"""
    return {
        "xml_url": "http://localhost:8000/static/exemplo_imoveis.xml",
        "descricao": "XML de exemplo com 3 imóveis para teste"
    }

# XML Importer (com tratamento de erro)
try:
    from services.xml_importer.importer import XMLImporter
    from config.examples.cliente_teste_local import TesteLocalXML
    
    @app.post("/import-xml-local")
    def import_xml_local():
        """Importar XML local de teste"""
        try:
            config = TesteLocalXML().get_config()
            
            importer = XMLImporter(
                config['cliente_id'],
                config['xml_url'], 
                config['xml_mapping']
            )
            
            resultado = importer.import_imoveis()
            return resultado
                
        except Exception as e:
            logger.error(f"Erro na importação local: {e}")
            return {"erro": str(e)}
    
    @app.get("/debug-xml-mapping")
    def debug_xml_mapping():
        """Debug do mapeamento XML"""
        try:
            config = TesteLocalXML().get_config()
            mapping = config['xml_mapping']
            
            return {
                "cliente_id": config['cliente_id'],
                "xml_url": config['xml_url'],
                "mapeamento": {
                    "id_field": mapping.id_field,
                    "codigo_field": mapping.codigo_field,
                    "titulo_field": mapping.titulo_field,
                    "tipo_field": mapping.tipo_field,
                    "preco_field": mapping.preco_field,
                    "cidade_field": mapping.cidade_field,
                    "estado_field": mapping.estado_field
                }
            }
        except Exception as e:
            return {"erro": str(e)}
            
except ImportError as e:
    logger.warning(f"XML Importer não disponível: {e}")

# Database (com tratamento de erro)
try:
    from core.database import create_tables, test_connection
    
    @app.post("/database/create-tables")
    def create_database_tables():
        """Criar tabelas do banco de dados"""
        try:
            create_tables()
            return {"status": "Tabelas criadas com sucesso"}
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            return {"erro": str(e)}
    
    @app.get("/database/test")
    def test_database():
        """Testar conexão com banco"""
        try:
            success = test_connection()
            return {"database": "OK" if success else "ERRO"}
        except Exception as e:
            return {"database": "ERRO", "erro": str(e)}
    
    # Endpoints de imóveis (só se banco estiver disponível)
    @app.get("/imoveis/{cliente_id}")
    def list_imoveis(cliente_id: str, limit: int = 10):
        """Listar imóveis de um cliente"""
        try:
            from core.database import get_db_session
            from models.imovel import Imovel
            
            with get_db_session() as db:
                imoveis = db.query(Imovel).filter(
                    Imovel.cliente_id == cliente_id,
                    Imovel.status == 'ativo'
                ).limit(limit).all()
                
                return {
                    "cliente_id": cliente_id,
                    "total": len(imoveis),
                    "imoveis": [imovel.to_dict() for imovel in imoveis]
                }
                
        except Exception as e:
            logger.error(f"Erro ao listar imóveis: {e}")
            return {"erro": str(e)}
    
    @app.get("/imoveis-stats/{cliente_id}")
    def imoveis_stats(cliente_id: str):
        """Estatísticas dos imóveis de um cliente"""
        try:
            from core.database import get_db_session
            from models.imovel import Imovel
            from sqlalchemy import func
            
            with get_db_session() as db:
                # Contar total
                total = db.query(func.count(Imovel.id)).filter(
                    Imovel.cliente_id == cliente_id
                ).scalar()
                
                # Contar ativos
                ativos = db.query(func.count(Imovel.id)).filter(
                    Imovel.cliente_id == cliente_id,
                    Imovel.status == 'ativo'
                ).scalar()
                
                return {
                    "cliente_id": cliente_id,
                    "total_geral": total,
                    "ativos": ativos,
                    "inativos": total - ativos
                }
                
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas: {e}")
            return {"erro": str(e)}
            
except ImportError:
    logger.warning("Database não disponível")

# Scheduler e Celery endpoints
try:
    from core.celery_app import celery_app
    from services.scheduler.import_tasks import import_client_manual, import_all_clients_daily
    from services.scheduler.tasks import health_check_clients, generate_daily_report
    
    @app.post("/scheduler/import-client/{cliente_id}")
    def schedule_client_import(cliente_id: str):
        """Agendar importação manual de um cliente"""
        try:
            task = import_client_manual.delay(cliente_id)
            
            return {
                "cliente_id": cliente_id,
                "task_id": task.id,
                "status": "agendado",
                "message": f"Importação do cliente {cliente_id} agendada",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao agendar importação: {e}")
            return {"erro": str(e)}
    
    @app.post("/scheduler/import-all")
    def schedule_all_imports():
        """Agendar importação de todos os clientes"""
        try:
            task = import_all_clients_daily.delay()
            
            return {
                "task_id": task.id,
                "status": "agendado",
                "message": "Importação de todos os clientes agendada",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao agendar importação geral: {e}")
            return {"erro": str(e)}
    
    @app.get("/scheduler/task-status/{task_id}")
    def get_task_status(task_id: str):
        """Verificar status de uma task"""
        try:
            task = celery_app.AsyncResult(task_id)
            
            return {
                "task_id": task_id,
                "status": task.status,
                "result": task.result if task.ready() else None,
                "info": task.info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"erro": str(e)}
    
    @app.get("/scheduler/active-tasks")
    def get_active_tasks():
        """Listar tasks ativas"""
        try:
            # Buscar tasks ativas
            inspect = celery_app.control.inspect()
            active_tasks = inspect.active()
            scheduled_tasks = inspect.scheduled()
            
            return {
                "active_tasks": active_tasks,
                "scheduled_tasks": scheduled_tasks,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"erro": str(e)}
    
    @app.post("/scheduler/health-check")
    def run_health_check():
        """Executar health check manual"""
        try:
            task = health_check_clients.delay()
            
            return {
                "task_id": task.id,
                "status": "agendado",
                "message": "Health check agendado",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"erro": str(e)}
    
    @app.get("/scheduler/daily-report")
    def get_daily_report():
        """Gerar relatório diário"""
        try:
            task = generate_daily_report.delay()
            
            return {
                "task_id": task.id,
                "status": "agendado",
                "message": "Relatório diário sendo gerado",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"erro": str(e)}
    
    @app.get("/scheduler/stats")
    def get_scheduler_stats():
        """Estatísticas do scheduler"""
        try:
            inspect = celery_app.control.inspect()
            stats = inspect.stats()
            
            return {
                "worker_stats": stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"erro": str(e)}
            
except ImportError as e:
    logger.warning(f"Scheduler não disponível: {e}")
    
    @app.post("/scheduler/import-client/{cliente_id}")
    def schedule_client_import(cliente_id: str):
        return {"erro": "Scheduler não disponível"}

# AI Matching endpoints
try:
    from services.ai_matching.matching_engine import MatchingEngine
    from models.lead import Lead, Matching
    from datetime import datetime
    import uuid
    
    @app.post("/leads/")
    def create_lead(lead_data: dict):
        """Criar novo lead"""
        try:
            with get_db_session() as db:
                # Gerar ID único
                lead_id = str(uuid.uuid4())
                
                # Criar lead
                new_lead = Lead(
                    id=lead_id,
                    cliente_id=lead_data.get('cliente_id', 'teste_local'),
                    nome=lead_data.get('nome'),
                    telefone=lead_data.get('telefone'),
                    email=lead_data.get('email'),
                    tipo_imovel=lead_data.get('tipo_imovel'),
                    categoria=lead_data.get('categoria'),
                    orcamento_min=lead_data.get('orcamento_min'),
                    orcamento_max=lead_data.get('orcamento_max'),
                    quartos_min=lead_data.get('quartos_min'),
                    quartos_max=lead_data.get('quartos_max'),
                    banheiros_min=lead_data.get('banheiros_min'),
                    area_min=lead_data.get('area_min'),
                    area_max=lead_data.get('area_max'),
                    vagas_min=lead_data.get('vagas_min'),
                    cidades_interesse=lead_data.get('cidades_interesse', []),
                    bairros_interesse=lead_data.get('bairros_interesse', []),
                    caracteristicas_desejadas=lead_data.get('caracteristicas_desejadas', []),
                    observacoes=lead_data.get('observacoes'),
                    origem=lead_data.get('origem', 'api'),
                    prioridade=lead_data.get('prioridade', 1)
                )
                
                db.add(new_lead)
                db.commit()
                
                logger.info(f"Lead criado: {lead_id}")
                return {
                    "status": "sucesso",
                    "lead_id": lead_id,
                    "message": "Lead criado com sucesso"
                }
                
        except Exception as e:
            logger.error(f"Erro ao criar lead: {e}")
            return {"erro": str(e)}
    
    @app.get("/leads/{cliente_id}")
    def list_leads(cliente_id: str, limit: int = 20):
        """Listar leads de um cliente"""
        try:
            with get_db_session() as db:
                leads = db.query(Lead).filter(
                    Lead.cliente_id == cliente_id,
                    Lead.status == 'ativo'
                ).limit(limit).all()
                
                return {
                    "cliente_id": cliente_id,
                    "total": len(leads),
                    "leads": [lead.to_dict() for lead in leads]
                }
                
        except Exception as e:
            logger.error(f"Erro ao listar leads: {e}")
            return {"erro": str(e)}
    
    @app.post("/matching/find-matches/{lead_id}")
    def find_matches(lead_id: str, limit: int = 10):
        """Encontrar matches para um lead"""
        try:
            engine = MatchingEngine()
            matches = engine.find_matches_for_lead(lead_id, limit)
            
            # Formatar resultado
            resultado = []
            for match in matches:
                imovel = match['imovel']
                scores = match['scores']
                
                resultado.append({
                    "imovel": imovel.to_dict(),
                    "scores": scores,
                    "compatibilidade": "alta" if scores['score_geral'] > 0.7 else "média" if scores['score_geral'] > 0.5 else "baixa"
                })
            
            return {
                "lead_id": lead_id,
                "total_matches": len(resultado),
                "matches": resultado,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar matches: {e}")
            return {"erro": str(e)}
    
    @app.get("/matching/matches/{lead_id}")
    def get_saved_matches(lead_id: str):
        """Buscar matches salvos de um lead"""
        try:
            with get_db_session() as db:
                matches = db.query(Matching).filter(
                    Matching.lead_id == lead_id
                ).order_by(Matching.score_geral.desc()).all()
                
                return {
                    "lead_id": lead_id,
                    "total_matches": len(matches),
                    "matches": [match.to_dict() for match in matches]
                }
                
        except Exception as e:
            logger.error(f"Erro ao buscar matches salvos: {e}")
            return {"erro": str(e)}
    
    @app.get("/matching/stats/{cliente_id}")
    def get_matching_stats(cliente_id: str):
        """Estatísticas de matching de um cliente"""
        try:
            with get_db_session() as db:
                from sqlalchemy import func
                
                # Total de leads
                total_leads = db.query(func.count(Lead.id)).filter(
                    Lead.cliente_id == cliente_id
                ).scalar()
                
                # Total de matches
                total_matches = db.query(func.count(Matching.id)).filter(
                    Matching.cliente_id == cliente_id
                ).scalar()
                
                # Matches por score
                matches_alta = db.query(func.count(Matching.id)).filter(
                    Matching.cliente_id == cliente_id,
                    Matching.score_geral > 0.7
                ).scalar()
                
                matches_media = db.query(func.count(Matching.id)).filter(
                    Matching.cliente_id == cliente_id,
                    Matching.score_geral.between(0.5, 0.7)
                ).scalar()
                
                return {
                    "cliente_id": cliente_id,
                    "total_leads": total_leads,
                    "total_matches": total_matches,
                    "matches_alta_compatibilidade": matches_alta,
                    "matches_media_compatibilidade": matches_media,
                    "matches_baixa_compatibilidade": total_matches - matches_alta - matches_media,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas: {e}")
            return {"erro": str(e)}
            
except ImportError as e:
    logger.warning(f"AI Matching não disponível: {e}")
    
    @app.post("/leads/")
    def create_lead(lead_data: dict):
        return {"erro": "Sistema de matching não disponível"}

@app.post("/test/create-sample-lead")
def create_sample_lead():
    """Criar lead de exemplo para testes"""
    try:
        sample_lead = {
            "cliente_id": "teste_local",
            "nome": "João Silva",
            "telefone": "(11) 99999-9999",
            "email": "joao.silva@email.com",
            "tipo_imovel": "apartamento",
            "categoria": "venda",
            "orcamento_min": 400000,
            "orcamento_max": 600000,
            "quartos_min": 2,
            "quartos_max": 3,
            "banheiros_min": 2,
            "area_min": 70,
            "area_max": 120,
            "vagas_min": 1,
            "cidades_interesse": ["São Paulo"],
            "bairros_interesse": ["Centro", "Jardins"],
            "caracteristicas_desejadas": ["piscina", "churrasqueira"],
            "observacoes": "Procuro apartamento com boa vista e piscina",
            "origem": "teste",
            "prioridade": 3
        }
        
        # Usar endpoint de criação
        from core.main import create_lead
        resultado = create_lead(sample_lead)
        
        return {
            "message": "Lead de teste criado",
            "lead_data": sample_lead,
            "resultado": resultado
        }
        
    except Exception as e:
        return {"erro": str(e)}
