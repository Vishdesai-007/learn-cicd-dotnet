using TodoApi;
using Xunit;

namespace TodoApi.Tests;

public class TodoServiceTests
{
    private readonly TodoService _svc = new();

    [Fact]
    public void GetAll_ReturnsSeededTodos()
    {
        var todos = _svc.GetAll();
        Assert.Equal(2, todos.Count);
    }

    [Fact]
    public void Add_IncreasesCount()
    {
        _svc.Add("New task");
        Assert.Equal(3, _svc.GetAll().Count);
    }

    [Fact]
    public void Add_ReturnsCorrectTitle()
    {
        var todo = _svc.Add("Write tests");
        Assert.Equal("Write tests", todo.Title);
        Assert.False(todo.IsComplete);
    }

    [Fact]
    public void Complete_MarksAsComplete()
    {
        var result = _svc.Complete(1);
        Assert.True(result);
        Assert.True(_svc.GetById(1)!.IsComplete);
    }

    [Fact]
    public void Complete_ReturnsFalse_WhenNotFound()
    {
        var result = _svc.Complete(999);
        Assert.False(result);
    }

    [Fact]
    public void GetById_ReturnsNull_WhenNotFound()
    {
        Assert.Null(_svc.GetById(999));
    }
}
