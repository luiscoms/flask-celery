from celery.result import AsyncResult
from flask import render_template, Blueprint, jsonify, request

from project.server.tasks import create_task, long_task

main_blueprint = Blueprint('main', __name__, )


@main_blueprint.route('/', methods=['GET'])
def home():
    return render_template('main/home.html')


@main_blueprint.route('/tasks', methods=['POST'])
def run_task():
    """Schedule a task
    ---
    parameters:
      - name: type
        in: body
        schema:
            $ref: '#/definitions/TaskType'
        required: true
    definitions:
      TaskType:
        type: object
        properties:
          type:
            type: integer
    responses:
      202:
        description: Task id
    """
    content = request.json
    task_type = content['type']
    task = create_task.delay(int(task_type))
    return jsonify({'task_id': task.id}), 202


@main_blueprint.route('/tasks/long', methods=['POST'])
def run_long_task():
    """Schedule a long task
    ---
    responses:
      202:
        description: Task id
    """
    task = long_task.delay()

    return jsonify({
        'task_id': task.id,
    }), 202


@main_blueprint.route('/tasks/<task_id>', methods=['GET'])
def get_status(task_id):
    """Get task status
    ---
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
    definitions:
      Task:
        type: object
        properties:
          task_id:
            type: string
          task_result:
            $ref: '#/definitions/TaskResult'
          task_status:
            type: string
      TaskResult:
        type: string
    responses:
      200:
        description: Actual task status
        schema:
          $ref: '#/definitions/Task'
        examples:
          rgb: ['red', 'green', 'blue']
    """
    task_result = AsyncResult(task_id)
    result = {
        'task_id': task_id,
        'task_status': task_result.status,
        'task_result': task_result.result
    }
    if isinstance(task_result.result, Exception):
        result['task_result'] = str(task_result.result)
    return jsonify(result)
