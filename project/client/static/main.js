// custom javascript

(function() {
  console.log('Sanity Check!');
})();

function handleClick(type) {
  const url = '/tasks' + (type == 3 ? '/long' : '')
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ type: type }),
  })
  .then(response => response.json())
  .then(data => followTask(data.task_id));
}

function fetchTaskStatus(taskID) {
  return fetch(`/tasks/${taskID}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(response => response.json());
}

function getStatus(taskID) {
  return fetchTaskStatus(taskID)
  .then(task => {
    const html = `
      <tr>
        <td>${taskID}</td>
        <td>${task.task_status}</td>
        <td>${task.task_result}</td>
      </tr>`;
    const newRow = document.getElementById('tasks').insertRow(0);
    newRow.innerHTML = html;

    return task;
  });
}

following_tasks = {};

function followTask(taskID) {
  const interval = setInterval(function() {
    getStatus(taskID).then(task => {
      if (task.task_status === 'SUCCESS' || task.task_status === 'FAILURE') {
        clearInterval(interval);
      }
    })
    .catch(err => {
      console.log(err);
      clearInterval(interval);
    });
  }, 1000);

  following_tasks[taskID] = interval;
}

function unfollowTask(taskID) {
    try {
      clearInterval(following_tasks[taskID]);
    } catch (e) {}
}