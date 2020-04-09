import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import werkzeug 

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selections):
    questions = [question.format() for question in selections]
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
	
	@app.after_request
	def after_request(response):
		"""
		Adds headers to every responses.
		"""

		response.headers.add(
			"Access-Control-Allow-Headers", "Content-Type,Authorization"
		)
		response.headers.add("Access-Control-Allow-Methods",
							"GET,POST,DELETE,OPTIONS")
		return response

	@app.route("/categories")
	def get_categories():
		"""
		Retrieves all categories.
		"""

		categories = list(map(Category.format, Category.query.all()))
		return jsonify(
			{
				"success": True,
				"categories": categories,
			}
		)

	
	@app.route("/questions")
	def get_questions():
		"""
		Retrieves all questions.
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

	@app.route("/questions/<int:id>", methods=["DELETE"])
	def delete_question(id):
		"""
		Deletes a question.
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

	@app.route("/questions", methods=["POST"])
	def post_question():

		"""
		Posts a new question or searches questions
		If searchTerm exists in the request body, search questions based on the search
		term. Otherwise, post a new question.
		"""

		try:
			body = request.get_json()
			search_term = body.get("searchTerm")

			if search_term is None:
				question = body.get("question")
				answer = body.get("answer")
				category = body.get("category")
				difficulty = body.get("difficulty")
				if None in (question, answer, category, difficulty):
					abort(400)
				new_question = Question(
					question=question,
					answer=answer,
					category=category,
					difficulty=difficulty,
				)
				new_question.insert()
				return jsonify({"success": True})
			else:
				selections = (
					Question.query.order_by(Question.id)
					.filter(Question.question.ilike(f"%{search_term}%"))
					.all()
				)
				current_questions = paginate_questions(request, selections)
				return jsonify(
					{
						"success": True,
						"questions": current_questions,
						"total_questions": len(selections),
						"current_category": None,
					}
				)
		except werkzeug.exceptions.BadRequest:
			abort(400)
		except Exception:
			abort(422)


	@app.route("/categories/<int:category_id>/questions")
	def get_questions_by_category(category_id):

		"""
		Retrieves all questions in one category.
		Retrieves all question in the category with the category id in url.
		"""

		category = Category.query.get(category_id)
		if category is None:
			abort(404)
		selections = (
			Question.query.order_by(Question.id).filter_by(category=category_id).all()
		)
		current_questions = paginate_questions(request, selections)
		return jsonify(
			{
				"success": True,
				"questions": current_questions,
				"total_questions": len(selections),
				"current_category": category_id,
			}
		)


	@app.route("/quizzes", methods=["POST"])
	def get_quiz_questions():
		"""
		Gets one random quiz question.
		Gets one random quiz question in the category indicated in request body. Make
		sure the random quiz is not in previous_questions.
		"""

		try:
			body = request.get_json()
			category_id = body.get("quiz_category")
			previous_questions = body.get("previous_questions")
			if category_id is None or previous_questions is None:
				abort(400)
			category = Category.query.get(category_id)
			if category is None:
				abort(404)
			question = (
				Question.query.order_by(func.random())
				.filter(
					~Question.id.in_(previous_questions),
					Question.category == category_id,
				)
				.first()
			)

			return jsonify({"success": True, "question": question.format()})
		except werkzeug.exceptions.BadRequest:
			abort(400)
		except werkzeug.exceptions.NotFound:
			abort(404)
		except Exception:
			abort(422)


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
