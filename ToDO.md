# SWTOR Armory Rebuild TODO

## 1. Clean Up Repository

* [x] Create one repository with:

```text
backend/
frontend/
```

* [x] Update `.gitignore` for backend venvs, frontend dependencies/builds, logs, env files, IDE files, and OS noise.
* [x] Remove already tracked local IDE files from git while keeping them locally:

    * [x] `.idea/.gitignore`
    * [x] `.idea/misc.xml`
    * [x] `.idea/modules.xml`
    * [x] `.idea/vcs.xml`
    * [x] `swtor_new_armory.iml`

* [x] Add a root `README.md` with setup and run commands.
* [x] Add `backend/.env.example`.
* [x] Add `frontend/.env.example`.
* [x] Document the old Odoo addon as the source of truth:

```text
/opt/odoo16c/custom/addons/swtor_armory/docs/rebuild-notes.md
/opt/odoo16c/custom/addons/swtor_armory/models/
/opt/odoo16c/custom/addons/swtor_armory/security/
/opt/odoo16c/custom/addons/swtor_armory/views/menu.xml
/opt/odoo16c/custom/addons/swtor_armory/__init__.py
```

## 2. Create Backend Skeleton

* [x] Create a FastAPI application under `backend/`.
* [x] Add backend dependencies:

    * [x] `fastapi`
    * [x] `uvicorn`
    * [x] `sqlalchemy`
    * [x] `alembic`
    * [x] `psycopg`
    * [x] `pydantic-settings`

* [x] Add app settings loaded from environment.
* [x] Add SQLAlchemy engine and session lifecycle.
* [x] Add Alembic configuration.
* [x] Add `GET /api/health`.
* [x] Add backend test setup.

## 3. Implement Authentication and Permissions

* [x] Add a user model.
* [x] Choose auth mechanism:

    * [x] JWT
    * [ ] cookie sessions
    * [ ] other

* [x] Implement login.
* [x] Implement current-user dependency.
* [x] Add user roles:

    * [x] normal user
    * [x] SWTOR admin

* [ ] Port Odoo owner-only record rules from `security/security.xml`.
* [ ] Enforce owner-only access for:

    * [ ] characters
    * [ ] loadouts
    * [ ] items
    * [ ] character crew skill relations
    * [ ] operation lockouts

* [ ] Enforce admin-only writes for reference data.
* [ ] Add tests proving users cannot read, edit, or delete another user's records.
* [ ] Add tests proving normal users cannot write reference data.

## 4. Build Core Database Models

* [x] Add shared model fields consistently:

    * [x] `id`
    * [x] `created_at`
    * [x] `updated_at`
    * [x] `owner_id` for user-owned records
    * [x] `active`

* [x] Create user-owned models:

    * [x] `Character`
    * [x] `Loadout`
    * [x] `Item`
    * [x] `CharacterCrewSkillRelation`
    * [x] `OperationLockout`

* [x] Create reference/admin-managed models:

    * [x] `CrewSkill`
    * [x] `Operation`
    * [x] `OperationDifficulty`
    * [x] `OperationBoss`
    * [x] `OriginStory`
    * [x] `ClassName`
    * [x] `Role`
    * [x] `Spec`
    * [x] `Title`
    * [x] `Vehicle`
    * [x] `Guild`, unless guilds become user-owned

* [x] Create many-to-many association tables:

    * [x] character class names
    * [x] character roles
    * [x] character loadouts
    * [x] character items
    * [x] character vehicles
    * [x] character titles
    * [x] class name roles
    * [x] crew skill related skills
    * [x] operation difficulties

* [x] Decide how binary fields are stored:

    * [x] PostgreSQL columns
    * [ ] uploaded files
    * [ ] static frontend assets

## 5. Port Character Rules

* [x] Add character fields from `models/character.py`.
* [x] Validate level is between 1 and 80.
* [x] Validate valor rank is between 1 and 100.
* [x] Allow no more than 2 class names.
* [x] Require class names to match origin story power type.
* [x] Allow no more than 3 crew skills.
* [x] Allow no more than 1 crafting crew skill.
* [x] Allow no more than 10 loadouts.
* [x] Derive display name from guild and character name.
* [x] Derive title count.
* [x] Derive mount count.
* [x] Derive crew skill count.
* [x] Derive available roles from selected class names.

## 6. Port Crew Skill Rules

* [x] Add crew skill fields from `models/crew_skill.py`.
* [x] Support skill types:

    * [x] crafting
    * [x] gathering
    * [x] mission

* [x] Validate character crew skill level is between 1 and 700.
* [x] Derive progress as `level / 700 * 100`.
* [x] Keep related skill behavior from the old addon.
* [x] Decide whether to preserve the old related-skill warning behavior or make it a hard validation.

## 7. Port Loadout Rules

* [x] Add loadout fields from `models/character.py`.
* [x] Support loadout types:

    * [x] PvE
    * [x] PvP

* [x] Validate Parsely loadout URLs.
* [x] Derive role from selected spec.
* [x] Derive Parsely iframe or replace it with a safer frontend preview/link.
* [x] Restrict available characters by spec, mirror spec, and role.

## 8. Port Item Rules

* [x] Add item fields from `models/item.py`.
* [x] Support item rarity values:

    * [x] common
    * [x] uncommon
    * [x] rare
    * [x] epic
    * [x] legendary

* [x] Support binding values:

    * [x] none
    * [x] bind on pickup
    * [x] bind on equip
    * [x] bind on legacy

* [x] Support cargo hold values:

    * [x] personal cargo hold
    * [x] legacy cargo hold
    * [x] guild cargo hold

* [x] Validate cargo bay range.
* [x] Ensure bound items stay in personal cargo hold.
* [x] Ensure legacy-bound items cannot be stored in guild cargo hold.

## 9. Port Operation and Lockout Rules

* [x] Add operation fields from `models/operation.py`.
* [x] Add operation difficulty fields.
* [x] Add operation boss fields.
* [x] Add operation lockout fields.
* [x] Sort lockouts by week descending.
* [x] Derive lockout display name from operation, difficulty, and reset week.
* [x] Derive lockout faction from character.
* [x] Derive completion rate from boss sequence and operation boss count.
* [x] Enforce unique lockout per character, boss, difficulty, and week.
* [x] Add default current-week filtering support for the frontend.

## 10. Port Titles, Vehicles, and Guilds

* [ ] Add title fields from `models/title.py`.
* [ ] Add vehicle fields from `models/vehicle.py`.
* [ ] Add guild fields from `models/guild.py`.
* [ ] Implement guild member count.
* [ ] Decide whether free-text character guild names should create guild records.
* [ ] Implement legacy title grant to all current user's characters.
* [ ] Implement legacy-bound vehicle grant to all current user's characters.
* [ ] Decide how vehicle icon URLs should be fetched and stored.

## 11. Seed Reference Data

* [ ] Convert Odoo `post_init_hook` data into idempotent seed scripts or Alembic data migrations.
* [ ] Seed crew skills.
* [ ] Seed operation difficulties:

    * [ ] SM / Story Mode
    * [ ] VM / Veteran Mode
    * [ ] MM / Master Mode

* [ ] Seed operations and bosses:

    * [ ] Eternity Vault
    * [ ] Karagga's Palace
    * [ ] Explosive Conflict
    * [ ] Terror From Beyond
    * [ ] Scum and Villainy
    * [ ] Dread Fortress
    * [ ] Dread Palace
    * [ ] The Ravagers
    * [ ] Temple of Sacrifice
    * [ ] Gods From the Machine
    * [ ] The Nature of Progress
    * [ ] R-4 Anomaly

* [ ] Seed origin stories.
* [ ] Seed class names.
* [ ] Seed roles:

    * [ ] Tank
    * [ ] Healer
    * [ ] DPS

* [ ] Seed all combat specs.
* [ ] Seed all mirror-spec relationships.
* [ ] Make repeated seed runs safe.

## 12. Build CRUD API

* [ ] Choose API response format for React Admin.
* [ ] Implement pagination.
* [ ] Implement sorting.
* [ ] Implement filtering.
* [ ] Implement reference lookup endpoints.
* [ ] Implement CRUD endpoints for:

    * [ ] characters
    * [ ] loadouts
    * [ ] items
    * [ ] crew skills
    * [ ] character crew skill relations
    * [ ] operations
    * [ ] operation difficulties
    * [ ] operation bosses
    * [ ] operation lockouts
    * [ ] origin stories
    * [ ] class names
    * [ ] roles
    * [ ] specs
    * [ ] titles
    * [ ] vehicles
    * [ ] guilds

* [ ] Add API tests for CRUD behavior.
* [ ] Add API tests for filters and sorting.
* [ ] Add API tests for constraints.
* [ ] Add API tests for permissions.

## 13. Create Frontend Shell

* [ ] Remove Vite starter UI.
* [ ] Set up React Admin.
* [ ] Configure API data provider.
* [ ] Configure auth provider.
* [ ] Add a SWTOR-focused app layout.
* [ ] Add navigation matching the old Odoo menu:

    * [ ] Characters
    * [ ] Items
    * [ ] Crew Skills
    * [ ] Operations
    * [ ] Classes
    * [ ] Titles
    * [ ] Mounts
    * [ ] Guilds

* [ ] Hide admin-only create/edit/delete actions from normal users.
* [ ] Keep backend permission checks as the real security boundary.

## 14. Build Frontend Resources

* [ ] Build character list.
* [ ] Build character kanban/card view equivalent.
* [ ] Build character create/edit form.
* [ ] Add character filters:

    * [ ] my characters
    * [ ] faction
    * [ ] server
    * [ ] guild
    * [ ] roles

* [ ] Build loadout list and form.
* [ ] Build item list and form.
* [ ] Build crew skill screens.
* [ ] Build character crew skill editor.
* [ ] Build operation screens.
* [ ] Build operation lockout screen with current-week default.
* [ ] Build origin story, class, role, and spec screens.
* [ ] Build title screens.
* [ ] Build mount screens.
* [ ] Build guild screens.

## 15. Migrate Existing Odoo Data

* [ ] Choose migration approach:

    * [ ] direct SQL export from Odoo PostgreSQL
    * [ ] Odoo shell/export script
    * [ ] CSV export/import

* [ ] Map Odoo record IDs to new record IDs.
* [ ] Preserve ownership:

```text
Odoo create_uid -> new owner_id
```

* [ ] Migrate user-owned data:

    * [ ] characters
    * [ ] loadouts
    * [ ] items
    * [ ] character crew skill relations
    * [ ] operation lockouts

* [ ] Migrate optional/reference additions:

    * [ ] guilds
    * [ ] titles
    * [ ] vehicles
    * [ ] uploaded icons/images if retained

* [ ] Add a verification script comparing record counts.
* [ ] Add a verification script checking important relationships.

## 16. Decide Achievement Scope

* [ ] Review `models/achievement.py`.
* [ ] Decide whether achievements are in scope for v1.
* [ ] If in scope, add achievement models:

    * [ ] achievement
    * [ ] achievement template
    * [ ] achievement category

* [ ] If out of scope, document that achievements are postponed.
* [ ] Note that achievements exist in the old models but are not loaded through the old manifest menus/security.

## 17. Prepare Deployment

* [ ] Add backend production run configuration.
* [ ] Add frontend production build command.
* [ ] Choose web server:

    * [ ] Nginx
    * [ ] Apache

* [ ] Serve `frontend/dist/` as static files.
* [ ] Reverse-proxy `/api` to FastAPI.
* [ ] Run Alembic migrations during deploy.
* [ ] Document PostgreSQL backup and restore.
* [ ] Document production environment variables.
