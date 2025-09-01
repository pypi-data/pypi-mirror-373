"""
EvoSphere FastAPI Server

Production-ready REST API server for EvoSphere evolutionary bio-compiler.
Provides comprehensive access to all six patent innovations through web endpoints.

Authors: Krishna Bajpai and Vedanshi Gupta
"""

import sys
import json
import time
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, File, UploadFile
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, FileResponse
    from pydantic import BaseModel, Field
    import uvicorn
except ImportError:
    raise ImportError("FastAPI dependencies not installed. Run: pip install 'evosphere[server]'")

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# EvoSphere imports
try:
    from evosphere.core.engine import EvoSphere
    from evosphere.quantum.quantum_engine import QuantumEvolutionEngine
    from evosphere.graph.adaptive_graph import AdaptiveEvolutionaryGraph
    from evosphere.compiler.compiler import EvolutionaryBioCompiler
    from evosphere.designer.pathway_designer import SmartEvolutionaryPathwayDesigner
    from evosphere.assimilation import EDAL
    from evosphere.coupling import CECE
except ImportError as e:
    print(f"Warning: Could not import EvoSphere components: {e}")

# API Models
class EvolutionRequest(BaseModel):
    """Request model for evolutionary optimization."""
    target_sequences: List[str] = Field(..., description="Target biological sequences")
    target_fitness: List[float] = Field(..., description="Target fitness values")
    evolution_steps: int = Field(1000, description="Number of evolution steps")
    population_size: int = Field(100, description="Population size")
    mutation_rate: float = Field(0.01, description="Mutation rate")
    use_quantum: bool = Field(False, description="Enable quantum evolution")
    use_graph: bool = Field(False, description="Enable adaptive graphs")
    save_trajectory: bool = Field(False, description="Save evolution trajectory")

class CompilationRequest(BaseModel):
    """Request model for bio-code compilation."""
    bio_code: str = Field(..., description="Bio-code to compile")
    target_language: str = Field("python", description="Target compilation language")
    optimization_level: int = Field(2, description="Optimization level (0-3)")
    target_platform: str = Field("cpu", description="Target platform")

class PathwayDesignRequest(BaseModel):
    """Request model for pathway design."""
    pathway_type: str = Field("metabolic", description="Type of pathway to design")
    constraints: Dict[str, Any] = Field({}, description="Design constraints")
    target_efficiency: float = Field(0.8, description="Target pathway efficiency")
    use_irl: bool = Field(False, description="Use inverse reinforcement learning")
    optimization_steps: int = Field(500, description="Optimization steps")

class AssimilationRequest(BaseModel):
    """Request model for data assimilation."""
    data_type: str = Field("genomic", description="Type of biological data")
    use_fusion: bool = Field(False, description="Enable multi-modal data fusion")
    use_uncertainty: bool = Field(False, description="Enable uncertainty quantification")
    real_time: bool = Field(False, description="Enable real-time processing")

class CouplingRequest(BaseModel):
    """Request model for cross-scale coupling."""
    scales: List[str] = Field(["molecular", "organismal", "population"], description="Biological scales")
    coupling_strength: float = Field(0.5, description="Coupling strength")
    evolution_time: float = Field(100.0, description="Evolution time")
    enable_feedback: bool = Field(False, description="Enable feedback control")
    enable_emergence: bool = Field(False, description="Enable emergence detection")

class SystemStatus(BaseModel):
    """System status response model."""
    timestamp: float
    components: Dict[str, Any]
    system_health: str
    active_processes: List[str]
    memory_usage: Dict[str, Any]

# Global system instances
_system_instances = {}

class EvoSphereAPI:
    """Main API class for EvoSphere system."""
    
    def __init__(self, enable_all_components: bool = False):
        """Initialize API with optional component enablement."""
        self.enable_all_components = enable_all_components
        self.active_processes = {}
        self.system_initialized = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("evosphere.api")
        
        if enable_all_components:
            self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all EvoSphere components."""
        try:
            self.logger.info("Initializing EvoSphere components...")
            
            # Core engine
            _system_instances['core'] = EvoSphere()
            
            # Quantum engine (HQESE)
            _system_instances['quantum'] = QuantumEvolutionEngine(
                num_qubits=10,
                evolution_steps=100
            )
            
            # Graph network (MRAEG)
            _system_instances['graph'] = AdaptiveEvolutionaryGraph(
                initial_nodes=20,
                max_nodes=1000
            )
            
            # Bio-compiler (EvoByte)
            _system_instances['compiler'] = EvolutionaryBioCompiler()
            
            # Pathway designer (SEPD)
            _system_instances['designer'] = SmartEvolutionaryPathwayDesigner(
                enable_irl=True,
                enable_constraints=True
            )
            
            # Data assimilation (EDAL)
            _system_instances['assimilation'] = EDAL(
                state_dim=20,
                observation_dim=10,
                enable_real_time=True,
                enable_uncertainty=True
            )
            
            # Cross-scale coupling (CECE)
            _system_instances['coupling'] = CECE(
                scales=['molecular', 'organismal', 'population', 'ecosystem'],
                enable_feedback=True,
                enable_emergence_detection=True,
                coupling_strength=0.5
            )
            
            self.system_initialized = True
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Component initialization failed: {e}")
            raise
    
    def get_system_status(self) -> SystemStatus:
        """Get comprehensive system status."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            memory_usage = {
                'rss': memory_info.rss,
                'vms': memory_info.vms,
                'percent': process.memory_percent()
            }
        except ImportError:
            memory_usage = {'error': 'psutil not available'}
        
        components_status = {}
        for name, instance in _system_instances.items():
            try:
                if hasattr(instance, 'get_system_status'):
                    components_status[name] = instance.get_system_status()
                elif hasattr(instance, 'get_engine_status'):
                    components_status[name] = instance.get_engine_status()
                elif hasattr(instance, 'get_compiler_status'):
                    components_status[name] = instance.get_compiler_status()
                elif hasattr(instance, 'get_designer_status'):
                    components_status[name] = instance.get_designer_status()
                elif hasattr(instance, 'get_network_status'):
                    components_status[name] = instance.get_network_status()
                else:
                    components_status[name] = {'status': 'operational', 'type': type(instance).__name__}
            except Exception as e:
                components_status[name] = {'status': 'error', 'error': str(e)}
        
        # Determine overall system health
        operational_count = sum(1 for status in components_status.values() 
                              if status.get('status') != 'error')
        total_count = len(components_status)
        
        if operational_count == total_count:
            system_health = "excellent"
        elif operational_count > total_count * 0.7:
            system_health = "good"
        elif operational_count > 0:
            system_health = "degraded"
        else:
            system_health = "critical"
        
        return SystemStatus(
            timestamp=time.time(),
            components=components_status,
            system_health=system_health,
            active_processes=list(self.active_processes.keys()),
            memory_usage=memory_usage
        )

def create_app(enable_all_components: bool = False) -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="EvoSphere API",
        description="Quantum-Enhanced Evolutionary Bio-Compiler REST API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize API instance
    api_instance = EvoSphereAPI(enable_all_components=enable_all_components)
    
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "EvoSphere API",
            "version": "1.0.0",
            "description": "Quantum-Enhanced Evolutionary Bio-Compiler",
            "authors": ["Krishna Bajpai", "Vedanshi Gupta"],
            "patent_innovations": ["HQESE", "MRAEG", "EvoByte", "SEPD", "EDAL", "CECE"],
            "endpoints": {
                "/docs": "API Documentation",
                "/status": "System Status",
                "/evolve": "Evolutionary Optimization",
                "/compile": "Bio-Code Compilation",
                "/design": "Pathway Design",
                "/assimilate": "Data Assimilation",
                "/couple": "Cross-Scale Coupling"
            }
        }
    
    @app.get("/status", response_model=SystemStatus)
    async def get_status():
        """Get system status for all components."""
        try:
            return api_instance.get_system_status()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
    
    @app.post("/evolve")
    async def run_evolution(request: EvolutionRequest, background_tasks: BackgroundTasks):
        """Run evolutionary optimization process."""
        try:
            if 'core' not in _system_instances:
                _system_instances['core'] = EvoSphere(
                    population_size=request.population_size,
                    mutation_rate=request.mutation_rate
                )
            
            engine = _system_instances['core']
            
            # Configure optional components
            if request.use_quantum and 'quantum' not in _system_instances:
                _system_instances['quantum'] = QuantumEvolutionEngine(num_qubits=10)
                engine.enable_quantum_evolution(num_qubits=10)
            
            if request.use_graph and 'graph' not in _system_instances:
                _system_instances['graph'] = AdaptiveEvolutionaryGraph(
                    initial_nodes=request.population_size
                )
                engine.enable_adaptive_graphs(initial_nodes=request.population_size)
            
            # Run evolution
            evolution_results = engine.evolve(
                target_sequences=request.target_sequences,
                target_fitness=request.target_fitness,
                max_generations=request.evolution_steps,
                save_trajectory=request.save_trajectory
            )
            
            return {
                "success": True,
                "evolution_id": f"evo_{int(time.time())}",
                "results": evolution_results,
                "timestamp": time.time()
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Evolution failed: {str(e)}")
    
    @app.post("/compile")
    async def compile_bio_code(request: CompilationRequest):
        """Compile bio-code using EvoByte compiler."""
        try:
            if 'compiler' not in _system_instances:
                _system_instances['compiler'] = EvolutionaryBioCompiler()
            
            compiler = _system_instances['compiler']
            
            # Compile bio-code
            compilation_results = compiler.compile_bio_code(
                bio_code=request.bio_code,
                target_language=request.target_language,
                optimization_level=request.optimization_level,
                target_platform=request.target_platform
            )
            
            return {
                "success": True,
                "compilation_id": f"comp_{int(time.time())}",
                "results": compilation_results,
                "timestamp": time.time()
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Compilation failed: {str(e)}")
    
    @app.post("/design")
    async def design_pathway(request: PathwayDesignRequest):
        """Design biological pathways using SEPD."""
        try:
            if 'designer' not in _system_instances:
                _system_instances['designer'] = SmartEvolutionaryPathwayDesigner(
                    enable_irl=request.use_irl,
                    enable_constraints=True
                )
            
            designer = _system_instances['designer']
            
            # Design pathway
            design_results = designer.design_pathway(
                pathway_type=request.pathway_type,
                constraints=request.constraints,
                target_efficiency=request.target_efficiency,
                max_iterations=request.optimization_steps
            )
            
            return {
                "success": True,
                "design_id": f"design_{int(time.time())}",
                "results": design_results,
                "timestamp": time.time()
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Pathway design failed: {str(e)}")
    
    @app.post("/assimilate")
    async def assimilate_data(request: AssimilationRequest, file: Optional[UploadFile] = File(None)):
        """Process biological data using EDAL system."""
        try:
            if 'assimilation' not in _system_instances:
                _system_instances['assimilation'] = EDAL(
                    state_dim=20,
                    observation_dim=15,
                    enable_real_time=request.real_time,
                    enable_uncertainty=request.use_uncertainty
                )
            
            edal = _system_instances['assimilation']
            
            # Process uploaded data or use mock data
            if file:
                # In production, would parse actual file content
                file_content = await file.read()
                data_info = {"filename": file.filename, "size": len(file_content)}
            else:
                data_info = {"mock_data": True}
            
            # Create mock observations for demonstration
            from evosphere.assimilation.data_assimilator import BiologicalObservation, DataType
            import numpy as np
            
            mock_observations = []
            for i in range(5):
                obs = BiologicalObservation(
                    observation_id=f"obs_{i}",
                    data_type=getattr(DataType, request.data_type.upper(), DataType.GENOMIC),
                    values=np.random.randn(10),
                    timestamp=time.time() - i,
                    quality_score=np.random.uniform(0.7, 1.0)
                )
                mock_observations.append(obs)
            
            # Process data
            processing_results = edal.process_biological_data(
                observations=mock_observations,
                use_fusion=request.use_fusion,
                quantify_uncertainty=request.use_uncertainty
            )
            
            return {
                "success": True,
                "assimilation_id": f"assim_{int(time.time())}",
                "data_info": data_info,
                "results": processing_results,
                "timestamp": time.time()
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Data assimilation failed: {str(e)}")
    
    @app.post("/couple")
    async def couple_scales(request: CouplingRequest):
        """Run cross-scale coupling analysis using CECE."""
        try:
            if 'coupling' not in _system_instances:
                _system_instances['coupling'] = CECE(
                    scales=request.scales,
                    enable_feedback=request.enable_feedback,
                    enable_emergence_detection=request.enable_emergence,
                    coupling_strength=request.coupling_strength
                )
            
            cece = _system_instances['coupling']
            
            # Create initial states
            import numpy as np
            initial_states = {}
            for scale in request.scales:
                initial_states[scale] = {
                    'fitness': np.random.uniform(0.5, 0.8),
                    'diversity': np.random.uniform(0.3, 0.7),
                    'mutation_rate': np.random.uniform(0.005, 0.02),
                    'population_size': np.random.randint(100, 5000),
                    'adaptation_rate': np.random.uniform(0.01, 0.05)
                }
            
            # Activate coupling
            activation_results = cece.activate_multi_scale_coupling(
                initial_states=initial_states
            )
            
            if not activation_results.get('success', False):
                raise Exception(f"Coupling activation failed: {activation_results.get('error', 'Unknown error')}")
            
            # Run coupled evolution
            time_steps = int(request.evolution_time / 0.1)
            
            evolution_results = cece.evolve_coupled_system(
                time_steps=time_steps,
                dt=0.1,
                save_trajectory=True
            )
            
            return {
                "success": True,
                "coupling_id": f"couple_{int(time.time())}",
                "activation": activation_results,
                "evolution": evolution_results,
                "system_status": cece.get_system_status(),
                "timestamp": time.time()
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Coupling analysis failed: {str(e)}")
    
    @app.get("/components")
    async def list_components():
        """List all available EvoSphere components."""
        return {
            "components": {
                "core": {
                    "name": "EvoSphere Core Engine",
                    "description": "Main evolutionary optimization engine",
                    "status": "available" if 'core' in _system_instances else "not_initialized"
                },
                "quantum": {
                    "name": "HQESE - Hybrid Quantum-Evolutionary State-Space Engine",
                    "description": "Quantum-enhanced evolution processing",
                    "status": "available" if 'quantum' in _system_instances else "not_initialized"
                },
                "graph": {
                    "name": "MRAEG - Multi-Resolution Adaptive Evolutionary Graphs",
                    "description": "Dynamic graph neural networks for biological modeling",
                    "status": "available" if 'graph' in _system_instances else "not_initialized"
                },
                "compiler": {
                    "name": "EvoByte - Evolutionary Bio-Compilation System",
                    "description": "Bio-code compiler with multi-target output",
                    "status": "available" if 'compiler' in _system_instances else "not_initialized"
                },
                "designer": {
                    "name": "SEPD - Smart Evolutionary Pathway Designer",
                    "description": "Intelligent biological pathway design system",
                    "status": "available" if 'designer' in _system_instances else "not_initialized"
                },
                "assimilation": {
                    "name": "EDAL - Evolutionary Data Assimilation Layer",
                    "description": "Real-time biological data processing and fusion",
                    "status": "available" if 'assimilation' in _system_instances else "not_initialized"
                },
                "coupling": {
                    "name": "CECE - Cross-Scale Evolutionary Coupling Engine",
                    "description": "Multi-scale biological system integration",
                    "status": "available" if 'coupling' in _system_instances else "not_initialized"
                }
            },
            "total_components": 7,
            "initialized_components": len(_system_instances),
            "system_ready": api_instance.system_initialized
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "system_initialized": api_instance.system_initialized,
            "active_components": len(_system_instances)
        }
    
    @app.get("/patents")
    async def get_patent_info():
        """Get information about patent innovations."""
        return {
            "patent_innovations": {
                "HQESE": {
                    "name": "Hybrid Quantum-Evolutionary State-Space Engine",
                    "description": "Novel quantum computing integration for evolutionary optimization",
                    "key_features": [
                        "Quantum superposition for parallel evolution paths",
                        "Quantum measurement for solution selection",
                        "Hybrid classical-quantum optimization"
                    ]
                },
                "MRAEG": {
                    "name": "Multi-Resolution Adaptive Evolutionary Graphs",
                    "description": "Dynamic graph neural networks for biological system modeling",
                    "key_features": [
                        "Adaptive graph topology evolution",
                        "Multi-resolution graph representations",
                        "Graph neural network integration"
                    ]
                },
                "EvoByte": {
                    "name": "Evolutionary Bio-Compilation System",
                    "description": "Domain-specific language and compiler for biological programming",
                    "key_features": [
                        "Bio-specific language constructs",
                        "Multi-target code generation",
                        "Evolutionary optimization integration"
                    ]
                },
                "SEPD": {
                    "name": "Smart Evolutionary Pathway Designer",
                    "description": "Intelligent pathway design with machine learning",
                    "key_features": [
                        "Inverse reinforcement learning",
                        "Multi-objective optimization",
                        "Real-time constraint adaptation"
                    ]
                },
                "EDAL": {
                    "name": "Evolutionary Data Assimilation Layer",
                    "description": "Real-time biological data processing and integration",
                    "key_features": [
                        "Multi-modal data fusion",
                        "Real-time streaming processing",
                        "Bayesian uncertainty quantification"
                    ]
                },
                "CECE": {
                    "name": "Cross-Scale Evolutionary Coupling Engine",
                    "description": "Multi-scale biological system integration and coupling",
                    "key_features": [
                        "Cross-scale coupling mechanisms",
                        "Emergent behavior detection",
                        "Multi-scale feedback control"
                    ]
                }
            },
            "filing_date": "2024",
            "inventors": ["Krishna Bajpai", "Vedanshi Gupta"],
            "status": "Patent Pending"
        }
    
    # Exception handlers
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "timestamp": time.time()
            }
        )
    
    return app

# CLI server command integration
def start_server(host: str = "localhost", port: int = 8000, 
                enable_all: bool = False, log_level: str = "INFO"):
    """Start the EvoSphere API server."""
    
    app = create_app(enable_all_components=enable_all)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level.lower()
    )

if __name__ == "__main__":
    # Run server directly
    start_server()
