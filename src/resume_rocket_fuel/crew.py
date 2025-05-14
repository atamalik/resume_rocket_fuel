from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import logging
import traceback
import yaml
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@CrewBase
class ResumeRocketFuel():
    """ResumeRocketFuel crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        try:
            logger.info(f"Loading configuration from {config_path}")
            # Get the absolute path to the config file
            base_path = Path(__file__).parent
            full_path = base_path / config_path
            
            logger.info(f"Full config path: {full_path}")
            
            if not full_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {full_path}")
                
            with open(full_path, 'r') as f:
                config = yaml.safe_load(f)
                
            if not config:
                raise ValueError(f"Empty configuration file: {config_path}")
                
            logger.info(f"Successfully loaded configuration from {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def __init__(self):
        logger.info("Initializing ResumeRocketFuel crew...")
        try:
            logger.info("Loading agents configuration...")
            self.agents_config = self._load_config(self.agents_config)
            logger.info("Loading tasks configuration...")
            self.tasks_config = self._load_config(self.tasks_config)
        except Exception as e:
            logger.error(f"Error initializing ResumeRocketFuel: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
   
    @agent
    def research_analyst(self) -> Agent:
        try:
            logger.info("Creating research_analyst agent...")
            if 'research_analyst' not in self.agents_config:
                raise KeyError("research_analyst configuration not found in agents.yaml")
            return Agent(
                config=self.agents_config['research_analyst'],
                verbose=True
            )
        except Exception as e:
            logger.error(f"Error creating research_analyst agent: {str(e)}")
            raise

    @agent
    def recruitment_analyst(self) -> Agent:
        try:
            logger.info("Creating recruitment_analyst agent...")
            if 'recruitment_analyst' not in self.agents_config:
                raise KeyError("recruitment_analyst configuration not found in agents.yaml")
            return Agent(
                config=self.agents_config['recruitment_analyst'],
                verbose=True
            )
        except Exception as e:
            logger.error(f"Error creating recruitment_analyst agent: {str(e)}")
            raise

    @agent
    def domain_expert(self) -> Agent:
        try:
            logger.info("Creating domain_expert agent...")
            if 'domain_expert' not in self.agents_config:
                raise KeyError("domain_expert configuration not found in agents.yaml")
            return Agent(
                config=self.agents_config['domain_expert'],
                verbose=True
            )
        except Exception as e:
            logger.error(f"Error creating domain_expert agent: {str(e)}")
            raise

    @agent
    def cv_editor(self) -> Agent:
        try:
            logger.info("Creating cv_editor agent...")
            if 'cv_editor' not in self.agents_config:
                raise KeyError("cv_editor configuration not found in agents.yaml")
            return Agent(
                config=self.agents_config['cv_editor'],
                verbose=True
            )
        except Exception as e:
            logger.error(f"Error creating cv_editor agent: {str(e)}")
            raise

    @agent
    def qa_manager(self) -> Agent:
        try:
            logger.info("Creating qa_manager agent...")
            if 'qa_manager' not in self.agents_config:
                raise KeyError("qa_manager configuration not found in agents.yaml")
            return Agent(
                config=self.agents_config['qa_manager'],
                verbose=True
            )
        except Exception as e:
            logger.error(f"Error creating qa_manager agent: {str(e)}")
            raise
    
    @task
    def upload_materials(self) -> Task:
        try:
            logger.info("Creating upload_materials task...")
            if 'upload_materials' not in self.tasks_config:
                raise KeyError("upload_materials configuration not found in tasks.yaml")
            return Task(
                config=self.tasks_config['upload_materials'],
            )
        except Exception as e:
            logger.error(f"Error creating upload_materials task: {str(e)}")
            raise

    @task
    def generate_company_profile_report(self) -> Task:
        try:
            logger.info("Creating generate_company_profile_report task...")
            if 'generate_company_profile_report' not in self.tasks_config:
                raise KeyError("generate_company_profile_report configuration not found in tasks.yaml")
            return Task(
                config=self.tasks_config['generate_company_profile_report'],
            )
        except Exception as e:
            logger.error(f"Error creating generate_company_profile_report task: {str(e)}")
            raise

    @task
    def analyze_cv_and_jd(self) -> Task:
        try:
            logger.info("Creating analyze_cv_and_jd task...")
            if 'analyze_cv_and_jd' not in self.tasks_config:
                raise KeyError("analyze_cv_and_jd configuration not found in tasks.yaml")
            return Task(
                config=self.tasks_config['analyze_cv_and_jd'],
            )
        except Exception as e:
            logger.error(f"Error creating analyze_cv_and_jd task: {str(e)}")
            raise
    
    @task
    def optimize_cv_for_domain(self) -> Task:
        try:
            logger.info("Creating optimize_cv_for_domain task...")
            if 'optimize_cv_for_domain' not in self.tasks_config:
                raise KeyError("optimize_cv_for_domain configuration not found in tasks.yaml")
            return Task(
                config=self.tasks_config['optimize_cv_for_domain'],
            )
        except Exception as e:
            logger.error(f"Error creating optimize_cv_for_domain task: {str(e)}")
            raise
    
    @task
    def merge_cv_enhancements(self) -> Task:
        try:
            logger.info("Creating merge_cv_enhancements task...")
            if 'merge_cv_enhancements' not in self.tasks_config:
                raise KeyError("merge_cv_enhancements configuration not found in tasks.yaml")
            return Task(
                config=self.tasks_config['merge_cv_enhancements'],
            )
        except Exception as e:
            logger.error(f"Error creating merge_cv_enhancements task: {str(e)}")
            raise

    @task
    def qa_review_final_cv(self) -> Task:
        try:
            logger.info("Creating qa_review_final_cv task...")
            if 'qa_review_final_cv' not in self.tasks_config:
                raise KeyError("qa_review_final_cv configuration not found in tasks.yaml")
            return Task(
                config=self.tasks_config['qa_review_final_cv'],
            )
        except Exception as e:
            logger.error(f"Error creating qa_review_final_cv task: {str(e)}")
            raise
        

    @crew
    def crew(self) -> Crew:
        """Creates the ResumeRocketFuel crew"""
        try:
            logger.info("Creating crew with agents and tasks...")
            if not hasattr(self, 'agents') or not self.agents:
                raise ValueError("No agents found. Make sure all agent methods are properly decorated with @agent")
            if not hasattr(self, 'tasks') or not self.tasks:
                raise ValueError("No tasks found. Make sure all task methods are properly decorated with @task")
                
            logger.info(f"Number of agents: {len(self.agents)}")
            logger.info(f"Number of tasks: {len(self.tasks)}")
            
            return Crew(
                agents=self.agents,
                tasks=self.tasks,
                process=Process.sequential,
                verbose=True,
            )
        except Exception as e:
            logger.error(f"Error creating crew: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
