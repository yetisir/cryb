import main
tasks = [
    main.get_github_api1,
    main.get_github_api2,
    main.query_google_api1,
    main.query_google_api2,
]

for i in range(100):
    # launching tasks one by one
    tasks[i % 2].apply_async(queue='github')
