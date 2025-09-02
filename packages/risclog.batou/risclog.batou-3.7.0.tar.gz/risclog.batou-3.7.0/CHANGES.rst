============================
Change log for risclog.batou
============================


3.7.0 (2025-09-02)
==================

- fix: Update libreoffice to NixOS 24.11 version.


3.6.4 (2025-08-27)
==================

- fix: Revert changes from 3.6.3 that broke docserver.


3.6.3 (2025-08-25)
==================

- fix: Update docserver requirements.


3.6.2 (2025-07-04)
==================

- fix: Reenable check for parallel requests in keycloaks bfd.
  (https://github.com/keycloak/keycloak/issues/33527)


3.6.1 (2025-06-26)
==================

- fix: Disable check for parallel requests in keycloaks bfd.
  (https://github.com/keycloak/keycloak/issues/33527)


3.6.0 (2025-06-24)
==================

- feat: Update keycloak to 26.2.5


3.5.1 (2025-06-16)
==================

- feat: Add flag to enable/disable tracelog for `proftpd`.


3.5.0 (2025-06-10)
==================

- feat: Add `last_login` date to Keycloak Users.
  (https://redmine.risclog.de/issues/35101)


3.4.10 (2025-05-15)
===================

- fix: Fix error if pkg is not pinned but editable.


3.4.9 (2025-05-15)
==================

- fix: Improve `Restart` component.


3.4.8 (2025-05-15)
==================

- fix: Restart docserver with the new `Restart` component.


3.4.7 (2025-05-14)
==================

- fix: Add `Restart` component to fix service restart issues on testing.


3.4.6 (2025-05-14)
==================

- fix: Indentation of config files.


3.4.5 (2025-03-20)
==================

- fix: Add `ignore_collisions` to `UserEnv`.
  (https://github.com/flyingcircusio/batou_ext/pull/216)


3.4.4 (2025-03-20)
==================

- fix: Update Docserver UserEnv.


3.4.3 (2025-03-14)
==================

- fix: Annotate unpinned packages in Requirements component.


3.4.2 (2025-03-14)
==================

- fix: Make sure local version pinnings override global ones.


3.4.1 (2025-03-13)
==================

- fix: Allow customizing jdk version for keycloak.


3.4.0 (2025-03-12)
==================

- feat: Add GH release download component.

- fix: Add more logging to `proftpd` configuration.


3.3.0 (2025-01-28)
==================

- fix: Finalize pypi secrets removal.


3.2.1 (2025-01-28)
==================

- fix: Remove pypi secrets from Requirements.


3.2.0 (2025-01-23)
==================

- feat: Update userenv default channel to 24.11.

- fix: Update pypi password.


3.1.0 (2024-10-28)
==================

- Switch from Python3.8 to 3.10


3.0.1 (2024-10-09)
==================

- feat: Default python versions for `appenv` to 3.10 and 3.11.


3.0.0 (2024-09-23)
==================

- fix: Syntax update for NixOS 24.05.


2.17.7 (2024-09-11)
===================

- feat: Fix `proftpd` configuration to allow connection via ssh keys (again).
  (https://redmine.risclog.de/issues/29669)



2.17.6 (2024-09-10)
===================

- feat: Fix `proftpd` configuration to allow connection via ssh keys.
  (https://redmine.risclog.de/issues/29669)


2.17.5 (2024-06-26)
===================

- Update docker integration to support external Keycloak better.
  (https://redmine.risclog.de/issues/30013)


2.17.4 (2024-06-26)
===================

- Update docker integration to support external Keycloak.
  (https://redmine.risclog.de/issues/30013)


2.17.3 (2024-06-12)
===================

- Update traefik config to support nginx in frontend.
  (https://redmine.risclog.de/issues/28427)


2.17.2 (2024-06-10)
===================

- Fix for devhost source integration.


2.17.1 (2024-05-31)
===================

- Fix ftp home dir, if service user is not `s-claimx`.

- Provide a default hostkey for sftp server.


2.17.0 (2024-05-30)
===================

- feat: Add `proftpd` server component.
  (https://redmine.risclog.de/issues/27755)


2.16.0 (2024-03-08)
===================

- feat: Add `UserEnv` hash to `Appenv` s requirements.txt to force rebuild if
  `UserEnv` changes.


2.15.0 (2024-01-26)
===================

- feat: Add ability to disable keycloak theme caching.

- feat: Allow configuring cronjobs for docker containers.


2.13.3 (2023-09-29)
===================

- fix: again deploying to dev environment where a Python3 us already installed.
  (https://redmine.risclog.de/issues/26404)



2.13.2 (2023-09-29)
===================

- fix: deploying to dev environment where a Python3 us already installed.
  (https://redmine.risclog.de/issues/26404)


2.13.1 (2023-09-29)
===================

- Fix brown bag release.


2.13.0 (2023-09-29)
===================

- feat: Add docserver component.
  (https://redmine.risclog.de/issues/26404)


2.12.0 (2023-07-06)
===================

- Finally get filebeat up and running.


2.11.2 (2023-07-06)
===================

- Installing filebeat via UserEnv is not necessary, nix uses the one provided
  by the system.


2.11.1 (2023-07-06)
===================

- Fix nixos channel url for filebeatenv.


2.11.0 (2023-07-06)
===================

- Provide a filebeatenv that installs a recent version of filebeat.


2.10.5 (2023-07-05)
===================

- Fix filebeat URL again.


2.10.4 (2023-07-05)
===================

- Fix filebeat URL.


2.10.3 (2023-06-30)
===================

- fix: Unify package names in requirements.txt.


2.10.2 (2023-06-30)
===================

- fix: Retrieving pinning lowercase.


2.10.1 (2023-06-22)
===================

- fix: Add dev requirements in local deployments.


2.10.0 (2023-06-22)
===================

- feat: Add component to update an AppEnv from a source components versions.


2.9.0 (2023-06-06)
==================

- feat: Allow setting custom env variables for docker containers.


2.8.6 (2023-05-23)
==================

- fix: Service port definition for non dev deployments.


2.8.5 (2023-05-23)
==================

- fix: Setting APM_ and VITE_ENVIRONMENT.


2.8.4 (2023-05-23)
==================

- fix: Docker deployment without traefik.


2.8.3 (2023-05-05)
==================

- fix: New filebeat host.


2.8.2 (2023-05-04)
==================

- fix: Some more bugs with filebeat from Nix.
  (https://redmine.risclog.de/issues/24734)


2.8.1 (2023-05-04)
==================

- fix: Cleanup old installations of filebeat.
  (https://redmine.risclog.de/issues/24734)

- fix: Path of `filebeat.nix` was not correct.
  (https://redmine.risclog.de/issues/24734)


2.8.0 (2023-05-04)
==================

- feat: Migrate filebeat to nix architecture.
  (https://redmine.risclog.de/issues/24734)


2.7.1 (2023-03-16)
==================

- fix: Change domain of now pypi back to pypi.claimx.net.
  (https://redmine.risclog.de/issues/19515)


2.7.0 (2023-03-15)
==================

- feat: Configure new claimx pypi.
  (https://redmine.risclog.de/issues/19515)


2.6.1 (2023-03-09)
==================

- Allow tags for git clones.


2.6.0 (2023-02-23)
==================

- Allow multiple `UserEnv` s.


2.5.5 (2023-02-23)
==================

- Don't add initial admin user if no admin password is configured.


2.5.4 (2023-02-23)
==================

- Allow settings the welcome theme for keycloak.


2.5.3 (2023-02-23)
==================

- Provide initial admin credentials to keycloak instance.


2.5.2 (2023-02-23)
==================

- Force settings keycloak hostnames.


2.5.1 (2023-02-23)
==================

- Force settings keycloak database password instead of using default "asdf".


2.5.0 (2023-02-23)
==================

- Add `keycloak` component.


2.4.0 (2023-02-22)
==================

- Add `bashenv` component.


2.3.0 (2023-02-21)
==================

- Add `docserver` component.


2.2.0 (2022-11-11)
==================

- Rename git multi action script to `gita` and allow specifying action.


2.1.0 (2022-11-07)
==================

- Allow settings `appenv-python-preference`.


2.0.0 (2022-10-13)
==================

- Set `clobber` in Git client which was introduced in batou 2.3b5.


1.10.2 (2022-07-05)
===================

- Allow multiple clients in keycloak deployment.


1.10.1 (2022-07-05)
===================

- Fix traefik pathprefix stripping.


1.10.0 (2022-07-04)
===================

- Install filebeat executable from newer nixos channel.


1.9.6 (2022-06-29)
==================

- Make docker service names more readable for systemd.


1.9.5 (2022-06-29)
==================

- Integrate keystore into docker containers.


1.9.4 (2022-06-28)
==================

- Readd `/swaggerui` path which is needed by old style containers.


1.9.3 (2022-06-28)
==================

- Changes to service.yml for TLS.


1.9.2 (2022-06-27)
==================

- Bugfix service.yml.


1.9.1 (2022-06-27)
==================

- Integrate new container structure.


1.9.0 (2022-06-27)
==================

- Add docker component.


1.8.1 (2022-04-07)
==================

- Use `batou_ext.ssh.ScanHost` to add github.com to known_hosts.


1.8.0 (2022-04-07)
==================

- Use `id_rsa_github` as rsa key filename for github source checkouts.


1.7.1 (2022-02-21)
==================

- Compatability to newer batou versions.


1.7.0 (2022-02-21)
==================

- Remove risclog private key, make it definable via deployment secrets.


1.6.2 (2022-02-09)
==================

- Allow installing package attributes via UserEnv.


1.6.1 (2022-02-09)
==================

- Bugfixes UserEnv


1.5 (2022-02-09)
================

- Add UserEnv component.


1.4 (2022-01-20)
================

- Add redis component.


1.3 (2022-01-20)
================

- Add disablenscd component that fixes DNS resolution problems on some VMs.


1.2 (2022-01-17)
================

- Add filebeat component.


1.1 (2022-01-17)
================

- Add source component that is compatible to appenv requirements.


1.0 (2022-01-17)
================

- initial release
