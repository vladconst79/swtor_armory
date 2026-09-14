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
* [x] Document the old Odoo addon as the historical reference:
  [vladconst79/swtor_armory_odoo](https://github.com/vladconst79/swtor_armory_odoo).

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

* [x] Port Odoo owner-only record rules from `security/security.xml`.
* [x] Enforce owner-only access for:

    * [x] characters
    * [x] loadouts
    * [x] items
    * [x] character crew skill relations
    * [x] operation lockouts

* [x] Enforce admin-only writes for reference data.
* [x] Add tests proving users cannot read, edit, or delete another user's records.
* [x] Add tests proving normal users cannot write reference data.

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

* [x] Add title fields from `models/title.py`.
* [x] Add vehicle fields from `models/vehicle.py`.
* [x] Add guild fields from `models/guild.py`.
* [x] Implement guild member count.
* [x] Decide whether free-text character guild names should create guild records.
* [x] Implement legacy title grant to all current user's characters.
* [x] Implement legacy-bound vehicle grant to all current user's characters.
* [x] Decide how vehicle icon URLs should be fetched and stored.

## 11. Seed Reference Data

* [x] Convert Odoo `post_init_hook` data into idempotent seed scripts or Alembic data migrations.
* [x] Seed crew skills.
* [x] Seed operation difficulties:

    * [x] SM / Story Mode
    * [x] VM / Veteran Mode
    * [x] MM / Master Mode

* [x] Seed operations and bosses:

    * [x] Eternity Vault
    * [x] Karagga's Palace
    * [x] Explosive Conflict
    * [x] Terror From Beyond
    * [x] Scum and Villainy
    * [x] Dread Fortress
    * [x] Dread Palace
    * [x] The Ravagers
    * [x] Temple of Sacrifice
    * [x] Gods From the Machine
    * [x] The Nature of Progress
    * [x] R-4 Anomaly

* [x] Seed origin stories.
* [x] Seed class names.
* [x] Seed roles:

    * [x] Tank
    * [x] Healer
    * [x] DPS

* [x] Seed all combat specs.
* [x] Seed all mirror-spec relationships.
* [x] Make repeated seed runs safe.

## 12. Build CRUD API

* [x] Choose API response format for React Admin.
* [x] Implement pagination.
* [x] Implement sorting.
* [x] Implement filtering.
* [x] Implement reference lookup endpoints.
* [x] Implement CRUD endpoints for:

    * [x] characters
    * [x] loadouts
    * [x] items
    * [x] crew skills
    * [x] character crew skill relations
    * [x] operations
    * [x] operation difficulties
    * [x] operation bosses
    * [x] operation lockouts
    * [x] origin stories
    * [x] class names
    * [x] roles
    * [x] specs
    * [x] titles
    * [x] vehicles
    * [x] guilds

* [x] Add API tests for CRUD behavior.
* [x] Add API tests for filters and sorting.
* [x] Add API tests for constraints.
* [x] Add API tests for permissions.

## 13. Create Frontend Shell

* [x] Remove Vite starter UI.
* [x] Set up React Admin.
* [x] Configure API data provider.
* [x] Configure auth provider.
* [x] Add a SWTOR-focused app layout.
* [x] Add navigation matching the old Odoo menu:

    * [x] Characters
    * [x] Items
    * [x] Crew Skills
    * [x] Operations
    * [x] Classes
    * [x] Titles
    * [x] Mounts
    * [x] Guilds

* [x] Hide admin-only create/edit/delete actions from normal users.
* [x] Keep backend permission checks as the real security boundary.

## 14. Build Frontend Resources

* [x] Build character list.
* [x] Build character kanban/card view equivalent.
* [x] Build character create/edit form.
* [x] Add character filters:

    * [x] my characters
    * [x] faction
    * [x] server
    * [x] guild
    * [x] roles

* [x] Build loadout list and form.
* [x] Build item list and form.
* [x] Build crew skill screens.
* [x] Build character crew skill editor.
* [x] Build operation screens.
* [x] Build operation lockout screen with current-week default.
* [x] Build origin story, class, role, and spec screens.
* [x] Build title screens.
* [x] Build mount screens.
* [x] Build guild screens.

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

## 16. Rework Frontend UX Toward Existing Odoo Quality Bar

Decision notes:

* [ ] Treat the current React Admin resource screens as functional scaffolding, not the final product UI.
* [ ] Keep the backend/API/auth/permissions/tests work; it is still useful and should not be thrown away.
* [ ] Reuse frontend plumbing where practical:

    * [ ] auth provider
    * [ ] data provider/API client
    * [ ] route/resource wiring where it still helps
    * [ ] validation and permission patterns

* [ ] Stop relying on generic React Admin list/show pages for core SWTOR domains.
* [ ] Use the existing Odoo UI screenshots as the design reference for density, layout, and domain presentation.

Target UX direction:

* [ ] Prefer top domain navigation over a long generic resource sidebar.
* [ ] Build dense, readable table views for high-volume records.
* [ ] Use meaningful SWTOR visual language:

    * [ ] role pills/colors
    * [ ] difficulty pills/colors
    * [ ] guild logos
    * [ ] mount/title/item icons where available
    * [ ] progress bars for completion/rank/progress fields

* [ ] Build entity pages around relationships, not raw fields.
* [ ] Use tabs for embedded related records:

    * [ ] character loadouts
    * [ ] character crew skills
    * [ ] character items
    * [ ] character titles
    * [ ] character mounts
    * [ ] character operation lockouts
    * [ ] guild characters
    * [ ] crew skill characters/related skills

Proof-of-direction step:

* [ ] Rebuild the Characters area first to match the old UI pattern:

    * [ ] top navigation shell
    * [ ] dense character list
    * [ ] role/class/faction/guild visual formatting
    * [ ] character detail page
    * [ ] embedded tab tables
    * [ ] create/edit controls that feel intentional, not generic

* [ ] Compare the rebuilt Characters area against the old Odoo screenshots.
* [ ] If the quality bar is reachable inside React Admin, continue replacing important pages with custom screens.
* [ ] If React Admin fights the target UX too much, switch to a custom Vite/React shell using the same backend API.
* [ ] Keep generic CRUD only for boring admin/reference data where it does not hurt the user experience.

## 17. Decide Achievement Scope

* [ ] Review `models/achievement.py`.
* [ ] Decide whether achievements are in scope for v1.
* [ ] If in scope, add achievement models:

    * [ ] achievement
    * [ ] achievement template
    * [ ] achievement category

* [ ] If out of scope, document that achievements are postponed.
* [ ] Note that achievements exist in the old models but are not loaded through the old manifest menus/security.

## 18. Prepare Deployment

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
