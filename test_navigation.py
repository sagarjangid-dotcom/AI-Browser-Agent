from agent.navigation import run_browser_task

command = input("Enter browser command: ")

result = run_browser_task(command)

print("\nRESULT:")
print(result)
