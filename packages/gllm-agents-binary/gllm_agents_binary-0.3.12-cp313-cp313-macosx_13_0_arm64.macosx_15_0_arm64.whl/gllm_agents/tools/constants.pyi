from _typeshed import Incomplete
from enum import Enum

BOSA_API_BASE_URL: Incomplete
BOSA_API_KEY: Incomplete
BOSA_FETCH_MAX_RETRIES: int

class Action(Enum):
    """Actions for BOSA Connector."""
    GITHUB = 'github'
    GOOGLE = 'google'
    GOOGLE_DRIVE = 'google_drive'
    GOOGLE_MAIL = 'google_mail'
    TWITTER = 'twitter'

class GitHubEndpoint(Enum):
    """GitHub endpoints for BOSA Connector."""
    INTEGRATIONS = 'integrations'
    USER_HAS_INTEGRATION = 'integration-exists'
    SUCCESS_AUTHORIZE_CALLBACK = 'success-authorize-callback'
    CREATE_ISSUE_HANDLER = 'create_issue'
    GET_ISSUE_HANDLER = 'get_issue'
    LIST_ISSUES = 'list_issues'
    LIST_ISSUES_COMMENTS = 'list_issues_comments'
    SEARCH_ALL_ISSUES = 'search_issues'
    GET_COMMITS = 'list_commits'
    SEARCH_COMMITS = 'search_commits'
    GET_COLLABORATORS = 'list_collaborators'
    GET_RELEASES = 'list_releases'
    GET_CONTRIBUTORS = 'list_contributors'
    GET_LANGUAGES = 'list_languages'
    SEARCH_CONTRIBUTIONS = 'search_contributions'
    LIST_PULL_REQUESTS = 'list_pull_requests'
    SEARCH_PR = 'search_pull_requests'
    GET_PULL = 'get_pull'
    GET_ALL_CONTRIBUTOR_COMMIT_ACTIVITIES = 'get_all_contributor_commit_activities'
    GET_COMMIT_ACTIVITY = 'get_the_last_year_of_commit_activity'
    GET_WEEKLY_COMMIT_COUNTS = 'get_weekly_commit_count '
    GET_USER_CONTRIBUTION_STATISTICS = 'get_user_contribution_statistics'
    LIST_PROJECT_ITEMS = 'list_project_items'
    LIST_PROJECTS = 'list_projects'

class GoogleDriveEndpoint(Enum):
    """Google Drive endpoints for BOSA Connector."""
    INTEGRATIONS = 'integrations'
    USER_HAS_INTEGRATION = 'integration-exists'
    SUCCESS_AUTHORIZE_CALLBACK = 'success-authorize-callback'
    SEARCH_FILES = 'search_files'
    GET_FILE = 'get_file'
    CREATE_FILE = 'create_file'
    CREATE_FOLDER = 'create_folder'
    UPDATE_FILE = 'update_file'
    UPDATE_FOLDER = 'update_folder'
    COPY_FILE = 'copy_file'
    DELETE_FILE = 'delete_file'
    SUMMARIZE_FOLDER_FILES_BY_TYPE = 'summarize_folder_files_by_type'
    SUMMARIZE_TOTAL_FILES_BY_TYPE = 'summarize_total_files_by_type'
    RECENT_FILES = 'list_recent_files_from_yesterday'
    CREATE_PERMISSION = 'create_permission'
    LIST_PERMISSIONS = 'list_permissions'
    GET_PERMISSION = 'get_permission'
    UPDATE_PERMISSION = 'update_permission'
    DELETE_PERMISSION = 'delete_permission'
    DOWNLOAD_FILE = 'download_file'

class GoogleDocsEndpoint(Enum):
    """Google Docs endpoints for BOSA Connector."""
    INTEGRATIONS = 'integrations'
    USER_HAS_INTEGRATION = 'integration-exists'
    SUCCESS_AUTHORIZE_CALLBACK = 'success-authorize-callback'
    GET_DOCUMENT = 'get_document'
    LIST_DOCUMENTS = 'list_documents'
    CREATE_DOCUMENT = 'create_document'
    UPDATE_DOCUMENT = 'update_document'
    COPY_CONTENT = 'copy_content'
    UPDATE_DOCUMENT_MARKDOWN = 'update_document_markdown'
    LIST_COMMENTS = 'list_comments'
    SUMMARIZE_COMMENTS = 'summarize_comments'

class GoogleEndpoint(Enum):
    """Google endpoints for BOSA Connector."""
    INTEGRATIONS = 'integrations'
    USER_HAS_INTEGRATION = 'integration-exists'
    SUCCESS_AUTHORIZE_CALLBACK = 'success-authorize-callback'
    USERINFO = 'userinfo'

class TwitterEndpoint(Enum):
    """Twitter endpoints for BOSA Connector."""
    INTEGRATIONS = 'integrations'
    USER_HAS_INTEGRATION = 'integration-exists'
    SUCCESS_AUTHORIZE_CALLBACK = 'success-authorize-callback'
    SEARCH = 'tweet_search'
    GET_TWEETS = 'get_tweets'
    GET_THREAD = 'get_thread'
    GET_USERS = 'get_users'

class GoogleMailEndpoint(Enum):
    """Google Mail endpoints for BOSA Connector."""
    INTEGRATIONS = 'integrations'
    USER_HAS_INTEGRATION = 'integration-exists'
    SUCCESS_AUTHORIZE_CALLBACK = 'success-authorize-callback'
    CREATE_DRAFT = 'create_draft'
    LIST_DRAFTS = 'list_drafts'
    SEND_DRAFT = 'send_draft'
    GET_DRAFT = 'get_draft'
    MODIFY_DRAFT = 'modify_draft'
    LIST_LABELS = 'list_labels'
    LABEL_STATS = 'label_stats'
    GET_LABEL_DETAILS = 'get_label_details'
    CREATE_LABELS = 'create_labels'
    MODIFY_LABELS = 'modify_labels'
    DELETE_LABELS = 'delete_labels'
    SEND_EMAIL = 'send_email'
    LIST_EMAILS = 'list_emails'
    GET_EMAIL_DETAILS = 'get_email_details'
    MODIFY_EMAIL = 'modify_email'
    DELETE_EMAIL = 'delete_email'
    TRASH_EMAIL = 'trash_email'
    UNTRASH_EMAIL = 'untrash_email'
    LIST_THREADS = 'list_threads'
    THREAD_DETAILS = 'thread_details'
    MODIFY_THREAD = 'modify_thread'
    GET_AUTO_REPLY = 'get_auto_reply'
    SET_AUTO_REPLY = 'set_auto_reply'
    GET_ATTACHMENT = 'get_attachment'
    USERINFO = 'userinfo'

class ActionEndpointMap:
    """Maps Action enums to their corresponding Endpoint enums."""
    MAP: dict[Action, type[Enum]]
