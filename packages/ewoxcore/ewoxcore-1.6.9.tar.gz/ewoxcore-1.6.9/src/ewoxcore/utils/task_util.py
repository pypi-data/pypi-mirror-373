from typing import Any, Optional, Dict, Tuple, Text, List
import asyncio


# https://docs.python.org/3/library/asyncio-task.html#creating-tasks
class TaskUtil:
    """ We keep a reference to the task until it is completed,
        this is to ensure the task does not get garbage collected while running."""
    _tasks:set[asyncio.Task] = set()


    @staticmethod
    def create_task(fn_task:Any) -> asyncio.Task:
        task:asyncio.Task = asyncio.create_task(fn_task)
        TaskUtil._tasks.add(task)

        # To prevent keeping references to finished tasks forever,
        # make each task remove its own reference from the set after
        # completion.
        task.add_done_callback(TaskUtil._tasks.discard)
        
        return task


    @staticmethod
    async def create_tasks(fn_tasks:List[Any], is_debug:bool=False) -> None:
        pending:set[asyncio.Task] = set()
        for fn_task in fn_tasks:
            task:asyncio.Task = TaskUtil.create_task(fn_task)
            pending.add(task)

        if (len(pending) == 0):
            return

        while pending:
            done, pending = await asyncio.wait(
                pending, return_when=asyncio.FIRST_COMPLETED)

            if (is_debug):
                result = done.pop().result()
                print(result)



if __name__ == "__main__":
    async def test_call(name:str, result:int, delay:int):
        print(name)
        await asyncio.sleep(delay)
        return result


    async def main():
        tasks:List[Any] = []
        tasks.append(test_call("TEST1", 1, 20))
        tasks.append(test_call("TEST2", 2, 3))
        tasks.append(test_call("TEST3", 3, 7))
        await TaskUtil.create_tasks(tasks, is_debug=True)

    asyncio.run(main())

