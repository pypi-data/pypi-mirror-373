from hero_base.state import State

state = State(
    workspace="tests/mock_workspace",
    history=[],
)

print(state.workspace)
print(state.working_dir)
print(state.log_dir)
print(state.set_storage("test", "test"))
print(state.get_storage("test"))