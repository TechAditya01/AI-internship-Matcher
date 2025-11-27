from flask import Blueprint, render_template, session, redirect, url_for, flash
from werkzeug.security import check_password_hash
import logging

bp = Blueprint("routes", __name__, template_folder="../templates")

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@bp.route("/")
def index():
    """Home page route."""
    user = session.get("user_info")  # Stored after successful OAuth
    LOG.info(f"Rendering home page. User logged in: {bool(user)}")
    
    try:
        return render_template("index.html", user=user)
    except Exception as e:
        LOG.error(f"Template render failed: {e}")
        return "<h2>Error: index.html missing or failed to render.</h2>"


@bp.route("/logout")
def logout():
    """Logs out the user and removes session tokens."""
    if session.get("user_info"):
        LOG.info(f"Logging out user: {session['user_info'].get('email')}")
        flash("You have been logged out.", "info")
    else:
        LOG.info("Logout request but no active session.")

    session.clear()
    return redirect(url_for("routes.index"))

@routes.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    user_type = request.form.get("user_type")

    user = get_user_by_email(email)

<<<<<<< HEAD
    if user and check_password_hash(user.password, password):
        session["user"] = user.email
        session["user_type"] = user_type
        flash("Login successful!", "success")
        return redirect(url_for("routes.dashboard"))  # adjust if needed
    else:
        flash("Invalid credentials", "danger")
        return redirect(url_for("routes.home"))
=======
@bp.route('/student/dashboard')
def student_dashboard():
    """Student dashboard"""
    if session.get('user_type') != 'student':
        return redirect(url_for('main.index'))
    
    student = Student.query.get(session['user_id'])
    if not student:
        return redirect(url_for('main.index'))
    
    # Get recent matches
    matches = Match.query.filter_by(student_id=student.id)\
                        .order_by(Match.overall_score.desc())\
                        .limit(10).all()
    
    return render_template('student_dashboard.html', student=student, matches=matches)

@bp.route('/department/profile')
def department_profile():
    """Department profile view page"""
    if session.get('user_type') != 'department':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

    department = Department.query.get(session.get('user_id'))
    if not department:
        flash("Department not found.", "danger")
        return redirect(url_for('main.index'))

    completeness_score, missing_fields = department.calculate_profile_completeness()

    return render_template(
        'department_profile_view.html',
        department=department,
        completeness_score=completeness_score,
        missing_fields=missing_fields
    )

@bp.route('/department/dashboard')
def department_dashboard():
    """Department dashboard"""
    if session.get('user_type') != 'department':
        return redirect(url_for('main.index'))
    
    department = Department.query.get(session['user_id'])
    if not department:
        return redirect(url_for('main.index'))
    
    # Get department's internships
    internships = Internship.query.filter_by(company_id=department.id).all()
    
    return render_template('department_dashboard.html', department=department, internships=internships)

@bp.route('/internship/create', methods=['GET', 'POST'])
def create_internship():
    """Create new internship"""
    if session.get('user_type') != 'department':
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title')
            description = request.form.get('description')
            sector = request.form.get('sector')
            location = request.form.get('location')
            required_skills = request.form.get('required_skills')
            preferred_course = request.form.get('preferred_course')
            min_cgpa = request.form.get('min_cgpa', type=float)
            year_of_study_requirement = request.form.get('year_of_study_requirement')
            total_positions = request.form.get('total_positions', type=int)
            duration_months = request.form.get('duration_months', type=int)
            stipend = request.form.get('stipend', type=float)
            
            # Handle application deadline
            application_deadline = None
            deadline_str = request.form.get('application_deadline')
            if deadline_str:
                try:
                    application_deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    pass
            
            # Affirmative action quotas
            rural_quota = request.form.get('rural_quota', type=int, default=0)
            sc_quota = request.form.get('sc_quota', type=int, default=0)
            st_quota = request.form.get('st_quota', type=int, default=0)
            obc_quota = request.form.get('obc_quota', type=int, default=0)
            
            # Validate required fields
            if not all([title, description, sector, total_positions]):
                flash('Please fill all required fields', 'error')
                return render_template('create_internship.html')
            
            # Create new internship
            internship = Internship(
                company_id=session['user_id'],
                title=title,
                description=description,
                sector=sector,
                location=location,
                required_skills=required_skills,
                preferred_course=preferred_course,
                min_cgpa=min_cgpa,
                year_of_study_requirement=year_of_study_requirement,
                total_positions=total_positions,
                duration_months=duration_months,
                stipend=stipend,
                application_deadline=application_deadline,
                rural_quota=rural_quota,
                sc_quota=sc_quota,
                st_quota=st_quota,
                obc_quota=obc_quota
            )
            
            db.session.add(internship)
            db.session.commit()
            
            flash('Internship created successfully!', 'success')
            return redirect(url_for('main.department_dashboard'))
            
        except Exception as e:
            logging.error(f"Error creating internship: {e}")
            flash('Failed to create internship. Please try again.', 'error')
            db.session.rollback()
    
    return render_template('create_internship.html')

@bp.route('/internship/edit/<int:internship_id>', methods=['GET', 'POST'])
def edit_internship(internship_id):
    """Edit existing internship"""
    if session.get('user_type') != 'department':
        return redirect(url_for('main.index'))
    
    # Get the internship and verify ownership
    internship = Internship.query.get_or_404(internship_id)
    if internship.company_id != session['user_id']:
        flash('Access denied.', 'error')
        return redirect(url_for('main.department_dashboard'))
    
    if request.method == 'POST':
        try:
            # Update internship with form data
            internship.title = request.form.get('title', internship.title)
            internship.description = request.form.get('description', internship.description)
            internship.sector = request.form.get('sector', internship.sector)
            internship.location = request.form.get('location', internship.location)
            internship.required_skills = request.form.get('required_skills', internship.required_skills)
            internship.preferred_course = request.form.get('preferred_course', internship.preferred_course)
            internship.min_cgpa = request.form.get('min_cgpa', type=float) or internship.min_cgpa
            internship.year_of_study_requirement = request.form.get('year_of_study_requirement', internship.year_of_study_requirement)
            internship.total_positions = request.form.get('total_positions', type=int) or internship.total_positions
            internship.duration_months = request.form.get('duration_months', type=int) or internship.duration_months
            internship.stipend = request.form.get('stipend', type=float) or internship.stipend
            
            # Handle application deadline
            deadline_str = request.form.get('application_deadline')
            if deadline_str:
                try:
                    internship.application_deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    pass
            
            # Update affirmative action quotas
            internship.rural_quota = request.form.get('rural_quota', type=int, default=0)
            internship.sc_quota = request.form.get('sc_quota', type=int, default=0)
            internship.st_quota = request.form.get('st_quota', type=int, default=0)
            internship.obc_quota = request.form.get('obc_quota', type=int, default=0)
            
            # Validate required fields
            if not all([internship.title, internship.description, internship.sector, internship.total_positions]):
                flash('Please fill all required fields', 'error')
                return render_template('create_internship.html', internship=internship, is_editing=True)
            
            db.session.commit()
            flash('Internship updated successfully!', 'success')
            return redirect(url_for('view_internship', internship_id=internship.id))
            
        except Exception as e:
            logging.error(f"Error updating internship: {e}")
            flash('Failed to update internship. Please try again.', 'error')
            db.session.rollback()
    
    return render_template('create_internship.html', internship=internship, is_editing=True)

@bp.route('/internship/delete/<int:internship_id>', methods=['POST'])
def delete_internship(internship_id):
    """Delete internship"""
    if session.get('user_type') != 'department':
        return redirect(url_for('main.index'))
    
    # Get the internship and verify ownership
    internship = Internship.query.get_or_404(internship_id)
    if internship.company_id != session['user_id']:
        flash('Access denied.', 'error')
        return redirect(url_for('main.department_dashboard'))
    
    try:
        # Check if there are any applications for this internship
        applications_count = Application.query.filter_by(internship_id=internship_id).count()
        
        if applications_count > 0:
            flash(f'Cannot delete internship. It has {applications_count} applications.', 'error')
            return redirect(url_for('edit_internship', internship_id=internship_id))
        
        # Delete related matches first
        Match.query.filter_by(internship_id=internship_id).delete()
        
        # Delete the internship
        db.session.delete(internship)
        db.session.commit()
        
        flash('Internship deleted successfully!', 'success')
        return redirect(url_for('main.department_dashboard'))
        
    except Exception as e:
        logging.error(f"Error deleting internship: {e}")
        flash('Failed to delete internship. Please try again.', 'error')
        db.session.rollback()
        return redirect(url_for('edit_internship', internship_id=internship_id))

@bp.route('/student/generate-matches')
def generate_matches():
    """Generate matches for current student"""
    if session.get('user_type') != 'student':
        return redirect(url_for('main.index'))
    
    try:
        student_id = session['user_id']
        # Verify student exists
        student = Student.query.get(student_id)
        if not student:
            logging.warning(f"Apply attempted with invalid session user_id={student_id}")
            flash('Session expired or user not found. Please login again.', 'error')
            return redirect(url_for('main.index'))
        matches = matching_engine.generate_matches_for_student(student_id)
        
        flash(f'Generated {len(matches)} new matches!', 'success')
        return redirect(url_for('main.view_matches'))
        
    except Exception as e:
        logging.error(f"Error generating matches: {e}")
        flash('Failed to generate matches. Please try again.', 'error')
        return redirect(url_for('main.student_dashboard'))

@bp.route('/student/matches')
def view_matches():
    """View all matches for current student"""
    if session.get('user_type') != 'student':
        return redirect(url_for('main.index'))
    
    student_id = session['user_id']
    matches = Match.query.filter_by(student_id=student_id)\
                        .order_by(Match.overall_score.desc()).all()
    
    return render_template('matches.html', matches=matches)

@bp.route('/student/apply/<int:internship_id>', methods=['POST'])
def apply_internship(internship_id):
    """Apply to an internship"""
    if session.get('user_type') != 'student':
        return redirect(url_for('main.index'))
    
    try:
        student_id = session['user_id']

        # Ensure internship exists
        internship = Internship.query.get(internship_id)
        if not internship:
            flash('Internship not found.', 'error')
            return redirect(url_for('main.view_matches'))

        # Check internship is active
        if not internship.is_active:
            flash('This internship is not accepting applications.', 'error')
            return redirect(url_for('main.view_matches'))

        # Check deadline
        if internship.application_deadline and internship.application_deadline < datetime.utcnow():
            flash('The application deadline for this internship has passed.', 'error')
            return redirect(url_for('main.view_matches'))

        # Check capacity
        if internship.filled_positions and internship.total_positions and internship.filled_positions >= internship.total_positions:
            flash('All positions for this internship are already filled.', 'error')
            return redirect(url_for('main.view_matches'))

        # Check if already applied
        existing_application = Application.query.filter_by(
            student_id=student_id,
            internship_id=internship_id
        ).first()

        if existing_application:
            flash('You have already applied to this internship', 'warning')
            return redirect(url_for('main.view_applications'))

        # Get form data
        cover_letter = request.form.get('cover_letter', '').strip()
        portfolio_url = request.form.get('portfolio_url', '').strip()
        additional_notes = request.form.get('additional_notes', '').strip()

        # Create application
        application = Application(
            student_id=student_id,
            internship_id=internship_id,
            cover_letter=cover_letter,
            portfolio_url=portfolio_url,
            additional_notes=additional_notes
        )

        db.session.add(application)
        db.session.commit()

        # If request came from AJAX (fetch/XHR), return JSON so frontend can stay on page
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json or ('application/json' in request.accept_mimetypes)
        if is_ajax:
            return jsonify({'success': True, 'message': 'Application submitted successfully!', 'application_id': application.id}), 201

        flash('Application submitted successfully!', 'success')
        return redirect(url_for('main.view_applications'))
        
    except Exception as e:
        logging.exception(f"Error applying to internship {internship_id} by student {session.get('user_id')}: {e}")
        # If AJAX, return JSON error
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json or ('application/json' in request.accept_mimetypes)
        db.session.rollback()
        if is_ajax:
            # In debug mode include exception message to help debugging
            if current_app.debug:
                return jsonify({'success': False, 'message': f'Server error while submitting application: {str(e)}'}), 500
            return jsonify({'success': False, 'message': 'Server error while submitting application. Please try again.'}), 500

        # Provide a helpful flash with minimal detail for non-AJAX
        flash('Failed to submit application due to a server error. Please try again or contact support.', 'error')
        return redirect(url_for('main.view_matches'))

@bp.route('/student/applications')
def view_applications():
    """View all applications for current student"""
    if session.get('user_type') != 'student':
        return redirect(url_for('main.index'))
    
    student_id = session['user_id']
    applications = Application.query.filter_by(student_id=student_id)\
                                  .order_by(Application.applied_at.desc()).all()
    
    return render_template('applications.html', applications=applications)

# Error handlers
@bp.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Google OAuth routes
@bp.route('/auth/google')
def google_auth():
    """Initiate Google OAuth"""
    user_type = request.args.get('type', 'student')

    # Block Google authentication for departments
    if user_type == 'department':
        flash('Google authentication is not available for departments. Please use email/password login.', 'warning')
        return redirect(url_for('main.index'))

    if user_type not in ['student']:
        flash('Invalid user type', 'error')
        return redirect(url_for('main.index'))

    # Store user type in session for callback
    session['oauth_user_type'] = user_type

    # Lazy import: avoid importing google auth libs at module load (can require cryptography)
    try:
        from app.oauth import create_google_flow
    except Exception as e:
        # Friendly message for missing dependency or import failure
        logging.error(f"Google OAuth not available: {e}")
        flash('Google authentication is not available on this server (missing dependencies).', 'error')
        return redirect(url_for('main.index'))

    flow = create_google_flow()
    if not flow:
        flash('Google authentication is not configured. Please contact administrator.', 'error')
        return redirect(url_for('main.index'))

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='select_account'
    )

    session['oauth_state'] = state
    return redirect(authorization_url)

@bp.route('/oauth2callback')
def oauth_callback():
    """Handle Google OAuth callback"""
    # Verify state parameter
    if 'oauth_state' not in session or request.args.get('state') != session['oauth_state']:
        flash('Invalid authentication state', 'error')
        return redirect(url_for('main.index'))
    
    user_type = session.get('oauth_user_type', 'student')
    
    # Lazy import of OAuth helpers
    try:
        from app.oauth import create_google_flow, handle_google_login, get_google_user_info
    except Exception as e:
        logging.error(f"Google OAuth helpers not available: {e}")
        flash('Google authentication is not available on this server (missing dependencies).', 'error')
        return redirect(url_for('main.index'))

    flow = create_google_flow()
    if not flow:
        flash('Authentication configuration error', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Get the authorization code and exchange for tokens
        flow.fetch_token(authorization_response=request.url)
        
        # Get user info from Google
        credentials = flow.credentials
        user_info = get_google_user_info(credentials.token)
        
        if not user_info:
            flash('Failed to get user information from Google', 'error')
            return redirect(url_for('main.index'))
        
        # Handle login/registration
        success, user_obj = handle_google_login(user_info, user_type)
        
        if success:
            session['user_type'] = user_type
            session['user_id'] = user_obj.id
            session['google_auth'] = True  # mark as logged in via Google
        
            # Check if this is a new user or profile is incomplete
            if user_type == "student":
                # Check if essential profile fields are missing
                if not user_obj.institution or not user_obj.course:
                    flash('Welcome! Please complete your profile to get started.', 'info')
                    return redirect(url_for('main.complete_student_profile'))
            elif user_type == "department":
                # Check if essential profile fields are missing  
                if not user_obj.ministry:
                    flash('Welcome! Please complete your department profile to start posting internships.', 'info')
                    return redirect(url_for('main.complete_department_profile'))
        
            # Profile is complete → go to dashboard
            flash(f"Welcome back, {user_obj.name}!", "success")
            if user_type == 'student':
                return redirect(url_for('main.student_dashboard'))
            elif user_type == 'department':
                return redirect(url_for('main.department_dashboard'))
            else:
                return redirect(url_for('main.index'))

        else:
            flash('Authentication failed. Please try again.', 'error')
            return redirect(url_for('main.index'))

            
    except Exception as e:
        logging.error(f"OAuth callback error: {e}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('main.index'))
    
    finally:
        # Clean up session
        session.pop('oauth_state', None)
        session.pop('oauth_user_type', None)

@bp.route('/complete-department-profile', methods=['GET', 'POST'])
def complete_department_profile():
    """Complete or edit department profile"""
    if session.get('user_type') != 'department':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    department = Department.query.get(session.get('user_id'))
    if not department:
        flash("Department not found.", "danger")
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            # Update department profile with form data
            department.name = request.form.get('name') or department.name
            department.ministry = request.form.get('ministry') or department.ministry
            department.department_type = request.form.get('department_type') or department.department_type
            department.location = request.form.get('location') or department.location
            department.description = request.form.get('description') or department.description
            department.contact_person = request.form.get('contact_person') or department.contact_person
            department.contact_phone = request.form.get('contact_phone') or department.contact_phone
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.department_profile'))
            
        except Exception as e:
            logging.error(f"Error updating department profile: {e}")
            flash('Failed to update profile. Please try again.', 'error')
            db.session.rollback()
    
    return render_template('complete_department_profile.html', department=department, is_editing=True)

# Department Application Management Routes
@bp.route('/department/applications')
def department_applications():
    """View all applications for department's internships"""
    if session.get('user_type') != 'department':
        return redirect(url_for('main.index'))
    
    dept_id = session['user_id']
    
    # Get all applications for this department's internships
    applications = Application.query.join(Internship)\
                                  .filter(Internship.company_id == dept_id)\
                                  .order_by(Application.applied_at.desc()).all()
    
    # Calculate match percentages for each application
    applications_with_match = []
    for application in applications:
        match_percentage = matching_engine.calculate_match_percentage(
            application.student, 
            application.internship
        )
        applications_with_match.append({
            'application': application,
            'match_percentage': match_percentage
        })
    
    return render_template('department_applications.html', 
                         applications_with_match=applications_with_match)

@bp.route('/internship/<int:internship_id>/applications')
def internship_applications(internship_id):
    """View applications for a specific internship"""
    if session.get('user_type') != 'department':
        return redirect(url_for('main.index'))
    
    # Get the internship and verify ownership
    internship = Internship.query.get_or_404(internship_id)
    if internship.department_id != session['user_id']:
        flash('Access denied.', 'error')
        return redirect(url_for('main.department_dashboard'))
    
    # Get applications for this internship
    applications = Application.query.filter_by(internship_id=internship_id)\
                                  .order_by(Application.applied_at.desc()).all()
    
    # Calculate match percentages for each application
    applications_with_match = []
    for application in applications:
        match_percentage = matching_engine.calculate_match_percentage(
            application.student, 
            internship
        )
        applications_with_match.append({
            'application': application,
            'match_percentage': match_percentage
        })
    
    return render_template('internship_applications.html', 
                         internship=internship, 
                         applications_with_match=applications_with_match)

@bp.route('/department/student/<int:student_id>')
def view_student_profile(student_id):
    """View a student's profile for application review"""
    if session.get('user_type') != 'department':
        flash('Access denied. Only departments can view student profiles.', 'error')
        return redirect(url_for('main.index'))
    
    student = Student.query.get_or_404(student_id)
    
    # Verify that the department has applications from this student for their internships
    dept_id = session['user_id']
    has_application = Application.query.join(Internship)\
                                     .filter(Internship.company_id == dept_id,
                                            Application.student_id == student_id).first()
    
    if not has_application:
        flash('Access denied. You can only view profiles of students who applied to your internships.', 'error')
        return redirect(url_for('main.department_dashboard'))
    
    # Calculate profile completeness
    completeness_score, missing_fields = student.calculate_profile_completeness()
    
    return render_template('student_profile_view.html', 
                         student=student,
                         completeness_score=completeness_score,
                         missing_fields=missing_fields,
                         from_department=True)

@bp.route('/application/<int:application_id>/update', methods=['POST'])
def update_application_status(application_id):
    """Update application status and send message to student"""
    if session.get('user_type') != 'department':
        flash('Access denied. Only departments can manage applications.', 'error')
        return redirect(url_for('main.index'))
    
    application = Application.query.get_or_404(application_id)
    
    # Verify that this application belongs to the department's internship
    if application.internship.company_id != session['user_id']:
        flash('Access denied. You can only manage applications for your own internships.', 'error')
        return redirect(url_for('main.department_dashboard'))
    
    try:
        # Update application status
        new_status = request.form.get('status')
        department_notes = request.form.get('department_notes', '')
        
        if new_status in ['pending', 'under_review', 'shortlisted', 'accepted', 'rejected']:
            # Handle position tracking before changing status
            old_status = application.status
            internship = application.internship
            
            # Update position count based on status change
            if old_status == 'accepted' and new_status != 'accepted':
                # Moving away from accepted - decrement filled positions
                if internship.filled_positions and internship.filled_positions > 0:
                    internship.filled_positions -= 1
            elif old_status != 'accepted' and new_status == 'accepted':
                # Moving to accepted - increment filled positions (check capacity)
                current_filled = internship.filled_positions or 0
                if current_filled >= internship.total_positions:
                    flash(f'Cannot accept more students. All {internship.total_positions} positions are filled.', 'error')
                    return redirect(url_for('main.internship_applications', internship_id=internship.id))
                internship.filled_positions = current_filled + 1
            
            # Update application details
            application.status = new_status
            application.department_notes = department_notes
            application.response_date = datetime.utcnow()
            
            db.session.commit()
            
            status_msg = {
                'pending': 'moved to pending',
                'under_review': 'moved to under review',
                'shortlisted': 'shortlisted',
                'accepted': 'accepted',
                'rejected': 'rejected'
            }
            
            flash(f'Application {status_msg[new_status]} successfully!', 'success')
        else:
            flash('Invalid status provided.', 'error')
            
    except Exception as e:
        logging.error(f"Error updating application status: {e}")
        flash('Failed to update application status. Please try again.', 'error')
        db.session.rollback()
    
    return redirect(url_for('main.internship_applications', internship_id=application.internship.id))

# Admin Routes
@bp.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if session.get('user_type') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    admin = Admin.query.get(session['user_id'])
    if not admin:
        return redirect(url_for('main.index'))
    
    # Get statistics
    total_students = Student.query.count()
    total_departments = Department.query.count()
    total_internships = Internship.query.count()
    total_applications = Application.query.count()
    
    # Get recent departments
    recent_departments = Department.query.order_by(Department.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html', 
                         admin=admin,
                         total_students=total_students,
                         total_departments=total_departments,
                         total_internships=total_internships,
                         total_applications=total_applications,
                         recent_departments=recent_departments)

@bp.route('/admin/departments', methods=['GET', 'POST'])
def manage_departments():
    """Create and manage departments"""
    if session.get('user_type') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            # Create new department
            email = request.form.get('email')
            password = request.form.get('password')
            name = request.form.get('name')
            ministry = request.form.get('ministry')
            department_type = request.form.get('department_type')
            location = request.form.get('location')
            description = request.form.get('description')
            contact_person = request.form.get('contact_person')
            contact_phone = request.form.get('contact_phone')
            
            # Check if email already exists
            existing_dept = Department.query.filter_by(email=email).first()
            if existing_dept:
                flash('Email already exists', 'error')
                return redirect(url_for('main.manage_departments'))
            
            # Create department
            department = Department(
                email=email,
                name=name,
                ministry=ministry,
                department_type=department_type,
                location=location,
                description=description,
                contact_person=contact_person,
                contact_phone=contact_phone,
                created_by=session['user_id']
            )
            department.set_password(password)
            
            db.session.add(department)
            db.session.commit()
            
            flash(f'Department "{name}" created successfully!', 'success')
            
        except Exception as e:
            logging.error(f"Error creating department: {e}")
            flash('Failed to create department. Please try again.', 'error')
            db.session.rollback()
    
    # Get all departments
    departments = Department.query.order_by(Department.created_at.desc()).all()
    
    return render_template('admin_departments.html', departments=departments)

@bp.route('/admin/departments/<int:dept_id>/toggle', methods=['POST'])
def toggle_department_status(dept_id):
    """Toggle department active status"""
    if session.get('user_type') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    department = Department.query.get_or_404(dept_id)
    department.is_active = not department.is_active
    
    try:
        db.session.commit()
        status = "activated" if department.is_active else "deactivated"
        flash(f'Department "{department.name}" {status} successfully!', 'success')
    except Exception as e:
        logging.error(f"Error toggling department status: {e}")
        flash('Failed to update department status.', 'error')
        db.session.rollback()
    
    return redirect(url_for('main.manage_departments'))

@bp.route('/admin/departments/<int:dept_id>/delete', methods=['POST'])
def delete_department(dept_id):
    """Delete department"""
    if session.get('user_type') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    department = Department.query.get_or_404(dept_id)
    
    try:
        # Check if department has active internships
        active_internships = Internship.query.filter_by(company_id=dept_id, is_active=True).count()
        if active_internships > 0:
            flash(f'Cannot delete department with {active_internships} active internships.', 'error')
            return redirect(url_for('main.manage_departments'))
        
        db.session.delete(department)
        db.session.commit()
        flash(f'Department "{department.name}" deleted successfully!', 'success')
        
    except Exception as e:
        logging.error(f"Error deleting department: {e}")
        flash('Failed to delete department.', 'error')
        db.session.rollback()
    
    return redirect(url_for('main.manage_departments'))

@bp.route('/generate-all-matches')
def generate_all_matches():
    """Admin function to generate matches for all students"""
    if session.get('user_type') != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
        
    try:
        total_matches = matching_engine.generate_all_matches()
        flash(f'Generated {total_matches} total matches!', 'success')
        
    except Exception as e:
        logging.error(f"Error generating all matches: {e}")
        flash('Failed to generate matches. Please try again.', 'error')
    
    return redirect(url_for('main.admin_dashboard'))

@bp.route('/internship/<int:internship_id>')
def view_internship(internship_id):
    """View internship details"""
    internship = Internship.query.get_or_404(internship_id)
    return render_template('internship_details.html', internship=internship)
>>>>>>> 9b96774 (updated code)


@bp.route("/health")
def health():
    """Health check route for deployment monitoring."""
    return "OK"
