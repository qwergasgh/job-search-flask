from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login.utils import login_required, current_user
from .forms import SearchForm, ParsingForm
from app.parsing import Parsing


blueprint_search = Blueprint('blueprint_search', 
                             __name__,
                             template_folder='templates', 
                             static_folder='static')


@blueprint_search.route('/', methods=['GET', 'POST'])
@login_required
def search():
    form_search = SearchForm()
    if form_search.validate_on_submit():
        return redirect(url_for('blueprint_report.report',
                                query_search=request.form.get('query_search'),
                                city=request.form.get('city'),
                                state=request.form.get('state'),
                                salary=request.form.get('salary')))
    return render_template('search_form.html', 
                           title='Job search', 
                           form_search=form_search)


@blueprint_search.route('/parsing', methods=['GET', 'POST'])
@login_required
def parsing():
    if current_user.is_administrator():
        form_parsing = ParsingForm()
        if form_parsing.validate_on_submit():
            p = Parsing(request.form.get('headhunter'),
                        request.form.get('stackoverflow'),
                        request.form.get('query_parsing').strip())
            p.parsing_vacancies()
        return render_template('parsing.html',
                               title='Job parsing',
                               form_parsing=form_parsing)
    else:
        return redirect(url_for('blueprint_search.search'))


@blueprint_search.route('/progress-parsing')
def progress():
    percentage = Parsing.get_percentage()
    if percentage == 100:
        Parsing.filling_database()
        Parsing.update_percentage(0)
        Parsing.vacancies.clear()
    return jsonify({'percentage': percentage}), 200


@blueprint_search.route('/stop-parsing', methods=['POST'])
def stop_parsing():
    Parsing.set_status_thread(False)
    Parsing.update_percentage(0)
    return jsonify({'parsing': 'stop'}), 200
