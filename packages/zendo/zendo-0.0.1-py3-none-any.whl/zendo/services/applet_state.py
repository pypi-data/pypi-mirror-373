from zendo.models import AppletState, db
from sqlalchemy.orm.attributes import flag_modified


def create_applet(
    id: str, user_id: int, applet_name: str, state_data: str | None = None
) -> tuple[bool, str, AppletState | None]:
    applet = AppletState(
        id=id,
        user_id=user_id,
        applet_name=applet_name,
        state_data=state_data,
    )
    try:
        db.session.add(applet)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return False, f"Failed to create AppletState: {e}", None
    return True, "AppletState created successfully", applet


def list_applets(user_id: int) -> tuple[bool, str, list[AppletState]]:
    try:
        applets = AppletState.query.filter_by(user_id=user_id).all()
        return True, "User applets retrieved successfully", applets
    except Exception as e:
        return False, f"Failed to retrieve user applets: {e}", []


def get_applet(user_id: int, applet_id: str) -> tuple[bool, str, AppletState | None]:
    try:
        applet = AppletState.query.filter_by(user_id=user_id, id=applet_id).first()
        if applet is None:
            return False, "AppletState not found", None
        return True, "AppletState retrieved successfully", applet
    except Exception as e:
        return False, f"Failed to retrieve AppletState: {e}", None


def update_applet(
    user_id: int, applet_id: str, state_data: dict | None = None
) -> tuple[bool, str, AppletState | None]:
    try:
        applet: AppletState = AppletState.query.filter_by(
            user_id=user_id, id=applet_id
        ).first()
        if applet is None:
            return False, "AppletState not found", None
        applet.state_data = state_data
        flag_modified(applet, "state_data")
        db.session.commit()
        return True, "AppletState updated successfully", applet
    except Exception as e:
        db.session.rollback()
        return False, f"Failed to update AppletState: {e}", None
