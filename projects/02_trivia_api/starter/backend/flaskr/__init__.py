import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 2


def paginate_questions(request, selections):
    questions = [question.format() for question in selections]
    # questions = list(map(question.format(),selections))
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    return questions[start:end]


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      """Adds headers to every responses."""

      response.headers.add(
          "Access-Control-Allow-Headers", "Content-Type,Authorization"
      )
      response.headers.add("Access-Control-Allow-Methods",
                           "GET,POST,DELETE,OPTIONS")
      return response

  @app.route("/categories")
  def get_categories():
      """Retrieves all categories."""

      categories = list(map(Category.format, Category.query.all()))
      return jsonify(
          {
              "success": True,
              "categories": categories,
          }
      )

  '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  @app.route("/questions")
  def get_questions():
      """Retrieves all questions.

      Retrieves all questions which are paginated in groups of 10.
      """

      selections = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selections)

      if len(current_questions) > 0:
          result = {
                  "success": True,
                  "questions": current_questions,
                  "total_questions": len(selections),
                  "categories": list(map(Category.format, Category.query.all())),
                  "current_category": None,
          }
          return jsonify(result)
      abort(404)



  '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''

  '''

  @app.route("/questions/<int:id>", methods=["DELETE"])
  def delete_question(id):
      """Deletes a question.

      Deletes a question with the id from url paramter.
      """
      question_data = Question.query.get(id)
      if question_data:

          Question.delete(question_data)
          result = {
                "success": True,
          }
          return jsonify(result)
      abort(404)

  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''


  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
  @app.errorhandler(404)
  def not_found(error):
      return (
          jsonify({"success": False, "error": 404, "message": "resource not found"}),
          404,
      )

  @app.errorhandler(422)
  def unprocessable(error):
      return (
          jsonify({"success": False, "error": 422, "message": "unprocessable"}),
          422,
      )

  @app.errorhandler(405)
  def method_not_allowed(error):
      return (
          jsonify({"success": False, "error": 405, "message": "method not allowed"}),
          405,
      )

  @app.errorhandler(400)
  def bad_request(error):
      return (
          jsonify({"success": False, "error": 400, "message": "bad request"}),
          400,
      )

  @app.errorhandler(500)
  def internal_server_error(error):
      return (
          jsonify(
              {"success": False, "error": 500, "message": "internal server error"}
          ),
          500,
      )

  return app
