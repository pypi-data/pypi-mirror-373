from .parameters import GraphState


# idea - methods router
def task_router (state: GraphState) -> str:

    if state['task']=='idea_generation':
        return 'maker'
    elif state['task']=='methods_generation':
        return 'methods'
    else:
        raise Exception('Wrong task choosen!')
    
# Idea maker - hater router
def router(state: GraphState) -> str:

    if state['idea']['iteration']<state['idea']['total_iterations']:
        return "hater"
    else: 
        return "__end__"
