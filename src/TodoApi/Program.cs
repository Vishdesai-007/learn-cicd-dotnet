using TodoApi;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSingleton<TodoService>();

var app = builder.Build();

app.MapGet("/health", () => Results.Ok(new { status = "healthy" }));

app.MapGet("/todos", (TodoService svc) => Results.Ok(svc.GetAll()));

app.MapGet("/todos/{id:int}", (int id, TodoService svc) =>
    svc.GetById(id) is Todo todo ? Results.Ok(todo) : Results.NotFound());

app.MapPost("/todos", (CreateTodoRequest req, TodoService svc) =>
{
    if (string.IsNullOrWhiteSpace(req.Title))
        return Results.BadRequest("Title is required.");
    var todo = svc.Add(req.Title);
    return Results.Created($"/todos/{todo.Id}", todo);
});

app.MapPut("/todos/{id:int}/complete", (int id, TodoService svc) =>
    svc.Complete(id) ? Results.NoContent() : Results.NotFound());

app.Run();

public record CreateTodoRequest(string Title);

// Make Program accessible to test project
public partial class Program { }
