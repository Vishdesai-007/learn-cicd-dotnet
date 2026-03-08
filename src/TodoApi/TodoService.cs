namespace TodoApi;

public class TodoService
{
    private readonly List<Todo> _todos = new()
    {
        new Todo(1, "Learn CI/CD", false),
        new Todo(2, "Build a pipeline", false),
    };

    private int _nextId = 3;

    public IReadOnlyList<Todo> GetAll() => _todos.AsReadOnly();

    public Todo? GetById(int id) => _todos.FirstOrDefault(t => t.Id == id);

    public Todo Add(string title)
    {
        var todo = new Todo(_nextId++, title, false);
        _todos.Add(todo);
        return todo;
    }

    public bool Complete(int id)
    {
        var index = _todos.FindIndex(t => t.Id == id);
        if (index < 0) return false;
        _todos[index] = _todos[index] with { IsComplete = true };
        return true;
    }
}
