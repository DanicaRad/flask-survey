# "http.client..." just appeared here... i think. what is this?
# from http.client import responses
from http.client import responses
from turtle import title
from flask import Flask, request, render_template, redirect, flash, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys, satisfaction_survey, personality_quiz

app = Flask(__name__)

app.config['SECRET_KEY'] = "Nigel"
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False 

@app.route('/home')
def home_page():
    title = satisfaction_survey.title
    instructions = satisfaction_survey.instructions
    return render_template('home.html', title=title, instructions=instructions)

@app.route('/')
def test_page():
    return render_template("home2.html", surveys=surveys)

@app.route('/session', methods=['POST', 'GET'])
def setup_session():
    session['responses'] = []
    return redirect('/questions/0')

@app.route('/questions/<int:num>')
def show_question_form(num):
    next_q = len(session['responses'])

    if next_q == len(satisfaction_survey.questions):
        flash("Survey is already complete, thank you!", "error")
        return redirect('/thankyou')
    elif num != next_q:
        flash("Invalid question number", "error")
        return redirect(f'/questions/{next_q}')
    else:
        question = satisfaction_survey.questions[num].question
        choices = satisfaction_survey.questions[num].choices
        return render_template('questions.html', num=num, question=question, choices=choices)

@app.route('/answers/<int:num>', methods=['POST'])
def get_survey_answers(num):
    responses = session['responses']
    response = list(request.form.values())
    responses.extend(response)
    session['responses'] = responses

    print(session['responses'])
    
    if num + 1 == len(satisfaction_survey.questions):
        return redirect('/thankyou')
    else:
        return redirect(f'/questions/{num + 1}')

@app.route('/thankyou')
def survey_completion_thankyou():
    return render_template('thankyou.html')

# ***********************************
# MULTIPLE SURVEYS ROUTES
# ***********************************

@app.route('/session/<survey>', methods=['POST', 'GET'])
def survey_session(survey):
    session[survey] = []
    return redirect(f'/{survey}/questions')

@app.route('/<survey>/questions/')
def show_questions(survey):
    num = len(session[survey])
    questions = surveys[survey].questions

    if request.cookies.get(f"{survey}"):
        flash(f"You've already submitted the {surveys[survey].title}", "error")
        return redirect(F'/{survey}/thankyou')

    if num == len(surveys[survey].questions):
        flash("Survey is already complete, thank you!", "error")
        return redirect(f'/{survey}/thankyou')
    else:
        return render_template('questions2.html', num=num, questions=questions, survey=survey)

@app.route('/<survey>/answers', methods=['POST'])
def get_surveys_answers(survey):
    print(f"REQUEST: {request}")

    responses = session[survey]
    num = len(responses)
    response = dict(request.form)
    responses.append(response)
    session[survey] = responses
    
    if num + 1 == len(surveys[survey].questions):
        return redirect(f'/{survey}/set-cookie')
    else:
        return redirect(f'/{survey}/questions')

@app.route('/<survey>/thankyou')
def mult_survey_thanks(survey):
    return render_template('thankyou2.html', survey=survey, surveys=surveys)

@app.route('/<survey>/set-cookie')
def set_completed_cookie(survey):
    content = redirect(f'/{survey}/thankyou')
    res = make_response(content)
    res.set_cookie(f"{survey}", "submitted")
    return res
