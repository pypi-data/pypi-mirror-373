"""
Core evaluation runner for Mini Control Arena.
"""

import importlib.util
from pathlib import Path
from typing import Any, Dict, Optional, Union

from inspect_ai import Task, eval
from inspect_ai.model import get_model
from inspect_ai.solver import solver, Solver, TaskState, Generate
from inspect_ai.agent import react, AgentState, AgentSubmit, AgentPrompt


def load_environment(
    environment_dir: str
) -> Any:
    """Load an environment from a directory.
    
    Args:
        environment_dir: Path to the environment directory containing environment.py
        
    Returns:
        An instance of the environment class found in the directory
        
    Raises:
        ValueError: If no Environment class is found in environment.py
    """
    path = Path(environment_dir).resolve()
    
    # Load environment.py
    spec = importlib.util.spec_from_file_location("environment", path / "environment.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Find the Environment class
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and name.endswith("Environment"):
            return obj()
    
    raise ValueError(f"No Environment class found in {environment_dir}/environment.py")


def run_eval(
    # Required
    environment_dir: str,
    model: str,
    # Task naming
    task_name: Optional[str] = None,
    # Parallelism
    max_connections: int = 10,
    # Errors and Limits
    time_limit: Optional[int] = 360,
    # Eval Logs
    log_dir: str = "./logs",
    log_format: str = "eval",
    no_log_realtime: bool = False,
    # Display
    display: str = "full",
    # Environment options (passed to environment methods)
    **environment_kwargs: Any
) -> Dict[str, Any]:
    """Run an evaluation on a specified environment.
    
    Args:
        environment_dir: Path to the environment directory to evaluate.
        model: Model used to evaluate tasks.
        
        task_name: Optional custom name for the task (defaults to "{dir}_{mode}_{side_task}").
        
        max_connections: Maximum number of concurrent connections to model provider.
        
        time_limit: Limit on total running time for each sample (in seconds).
        
        log_dir: Directory for log files.
        log_format: Format for writing log files. Values: eval, json.
        no_log_realtime: Do not log events in realtime (affects live viewing of logs).
        
        display: Display type. Values: full, conversation, rich, plain, log, none.
        
        **environment_kwargs: Environment-specific options passed to environment methods.
            All parameters starting with 'environment_' are passed to your environment.
            Common parameters include:
            - environment_mode: Evaluation mode (e.g., "honest", "attack")
            - environment_samples: Sample selection within the dataset
            - environment_max_tests: Max test cases per problem
            - environment_test_timeout: Timeout per test case
            
    Returns:
        EvalLog object containing evaluation results from Inspect AI
    """
    # Load environment
    environment = load_environment(environment_dir)
    
    # Get dataset, tools, scorer, etc. from environment
    dataset = environment.get_dataset(**environment_kwargs)
    tools = environment.get_tools(**environment_kwargs)
    scorer = environment.get_scorer(**environment_kwargs)
    sandbox = environment.get_sandbox_config()
    
    # Create solver using react agent
    @solver
    def control_solver() -> Solver:
        async def solve(
            state: TaskState,
            generate: Generate
        ) -> TaskState:
            # Run environment setup
            setup_solver = environment.setup_environment(state=state, **environment_kwargs)
            if setup_solver:
                state = await setup_solver(state, generate)
            
            # Get prompt from environment
            prompt = environment.get_system_prompt(**environment_kwargs)
            
            # Use react agent with only the environment's prompt (no defaults)
            agent = react(
                prompt=AgentPrompt(
                    instructions=prompt,
                    assistant_prompt=None,  # Disable default assistant prompt
                    handoff_prompt=None,    # Disable default handoff prompt
                    submit_prompt=None      # Disable default submit prompt
                ),
                model=model,
                tools=tools,
                submit=AgentSubmit(keep_in_messages=True)  # Keep submit in message history
            )
            
            # Run the agent with AgentState
            agent_state = AgentState(messages=state.messages)
            await agent(agent_state)
            
            # Update the state with agent's results
            state.messages = agent_state.messages
            state.output = agent_state.output
            
            return state
        
        return solve
    
    # Create and run task
    # Use custom task name if provided, otherwise create descriptive default
    if task_name is None:
        dir_name = Path(environment_dir).name
        mode = environment_kwargs.get("environment_mode", "honest")
        
        # Build task name components
        name_parts = [dir_name, mode]
        
        # Add side task name if in attack mode
        if mode == "attack":
            side_task = environment_kwargs.get("environment_side_task", None)
            if side_task:
                name_parts.append(side_task)
        
        task_name = "_".join(name_parts)
    
    task = Task(
        name=task_name,
        dataset=dataset,
        solver=control_solver(),
        scorer=scorer,
        sandbox=sandbox
    )
    
    # Run evaluation
    return eval(
        task,
        model=get_model(model),
        max_connections=max_connections,
        time_limit=time_limit,
        log_dir=log_dir,
        log_format=log_format,
        no_log_realtime=no_log_realtime,
        display=display
    )