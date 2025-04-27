from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app
from app.forms import ProjectForm
from models import Project
from app import db
import os
from werkzeug.utils import secure_filename

project_bp = Blueprint('project', __name__)

def save_file(file):
    if not file:
        return None
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    # Убедимся, что папка существует
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)
    return filename

@project_bp.route('/')
def home():
    return render_template('home.html')

@project_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    query = request.args.get('q', '')

    if query:
        projects = Project.query.filter(
            Project.user_id == user_id,
            (Project.title.ilike(f"%{query}%")) | (Project.description.ilike(f"%{query}%"))
        ).all()
    else:
        projects = Project.query.filter_by(user_id=user_id).all()

    return render_template('dashboard.html', projects=projects, query=query)

@project_bp.route('/project/add', methods=['GET', 'POST'])
def add_project():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    form = ProjectForm()
    if form.validate_on_submit():
        filename = save_file(form.image.data)
        project = Project(
            title=form.title.data,
            description=form.description.data,
            image_filename=filename,
            user_id=session['user_id']
        )
        db.session.add(project)
        db.session.commit()
        flash('Project added successfully.')
        return redirect(url_for('project.dashboard'))
    return render_template('add_project.html', form=form)

@project_bp.route('/project/<int:id>/edit', methods=['GET', 'POST'])
def edit_project(id):
    project = Project.query.get_or_404(id)
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        if form.image.data:
            filename = save_file(form.image.data)
            project.image_filename = filename
        db.session.commit()
        flash('Project updated.')
        return redirect(url_for('project.dashboard'))
    return render_template('edit_project.html', form=form)

@project_bp.route('/project/<int:id>/delete')
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted.')
    return redirect(url_for('project.dashboard'))

@project_bp.route('/project/<int:id>')
def project_detail(id):
    project = Project.query.get_or_404(id)
    return render_template('project_detail.html', project=project)
