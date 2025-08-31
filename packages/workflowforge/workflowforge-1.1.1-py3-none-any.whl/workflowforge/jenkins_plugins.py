"""Jenkins plugins and VCS support for WorkflowForge."""

from pydantic import BaseModel, Field


class GitCheckout(BaseModel):
    """Git checkout configuration."""

    url: str = Field(..., description="Git repository URL")
    branch: str = Field(default="main", description="Branch to checkout")
    credentials_id: str | None = Field(None, description="Jenkins credentials ID")
    shallow: bool | None = Field(None, description="Shallow clone")
    depth: int | None = Field(None, description="Clone depth")

    def to_step(self) -> str:
        """Convert to Jenkins step."""
        step = "checkout scm: [$class: 'GitSCM', "
        step += f"branches: [[name: '{self.branch}']], "
        step += f"userRemoteConfigs: [[url: '{self.url}'"
        if self.credentials_id:
            step += f", credentialsId: '{self.credentials_id}'"
        step += "]]"
        if self.shallow:
            step += (
                f", extensions: [[$class: 'CloneOption', "
                f"shallow: {str(self.shallow).lower()}"
            )
            if self.depth:
                step += f", depth: {self.depth}"
            step += "]]"
        step += "]"
        return step


class DockerPlugin(BaseModel):
    """Docker plugin configuration."""

    image: str = Field(..., description="Docker image")
    args: str | None = Field(None, description="Docker run arguments")
    registry_url: str | None = Field(None, description="Docker registry URL")
    credentials_id: str | None = Field(None, description="Registry credentials")

    def to_step(self, command: str) -> str:
        """Convert to Docker step."""
        step = f"docker.image('{self.image}')"
        if self.registry_url or self.credentials_id:
            step += ".withRegistry("
            if self.registry_url:
                step += f"'{self.registry_url}'"
            if self.credentials_id:
                if self.registry_url:
                    step += f", '{self.credentials_id}'"
                else:
                    step += f"null, '{self.credentials_id}'"
            step += ")"
        step += f".inside('{self.args or ''}') {{ {command} }}"
        return step


class SlackNotification(BaseModel):
    """Slack notification plugin."""

    channel: str = Field(..., description="Slack channel")
    message: str = Field(..., description="Message to send")
    color: str | None = Field(None, description="Message color")
    token_credential_id: str | None = Field(
        None, description="Slack token credential ID"
    )

    def to_step(self) -> str:
        """Convert to Slack step."""
        step = f"slackSend channel: '{self.channel}', message: '{self.message}'"
        if self.color:
            step += f", color: '{self.color}'"
        if self.token_credential_id:
            step += f", tokenCredentialId: '{self.token_credential_id}'"
        return step


class EmailNotification(BaseModel):
    """Email notification plugin."""

    to: str = Field(..., description="Email recipients")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body")
    attach_log: bool | None = Field(None, description="Attach build log")

    def to_step(self) -> str:
        """Convert to email step."""
        step = (
            f"emailext to: '{self.to}', subject: '{self.subject}', body: '{self.body}'"
        )
        if self.attach_log:
            step += f", attachLog: {str(self.attach_log).lower()}"
        return step


class ArtifactArchiver(BaseModel):
    """Artifact archiver plugin."""

    artifacts: str = Field(..., description="Artifacts pattern")
    allow_empty: bool | None = Field(None, description="Allow empty archive")
    fingerprint: bool | None = Field(None, description="Fingerprint artifacts")
    only_if_successful: bool | None = Field(
        None, description="Only if build successful"
    )

    def to_step(self) -> str:
        """Convert to archive step."""
        step = f"archiveArtifacts artifacts: '{self.artifacts}'"
        if self.allow_empty is not None:
            step += f", allowEmptyArchive: {str(self.allow_empty).lower()}"
        if self.fingerprint is not None:
            step += f", fingerprint: {str(self.fingerprint).lower()}"
        if self.only_if_successful is not None:
            step += f", onlyIfSuccessful: {str(self.only_if_successful).lower()}"
        return step


class JUnitPublisher(BaseModel):
    """JUnit test results publisher."""

    test_results: str = Field(..., description="Test results pattern")
    allow_empty: bool | None = Field(None, description="Allow empty results")
    keep_long_stdio: bool | None = Field(None, description="Keep long stdio")

    def to_step(self) -> str:
        """Convert to JUnit step."""
        step = f"junit testResults: '{self.test_results}'"
        if self.allow_empty is not None:
            step += f", allowEmptyResults: {str(self.allow_empty).lower()}"
        if self.keep_long_stdio is not None:
            step += f", keepLongStdio: {str(self.keep_long_stdio).lower()}"
        return step


# Factory functions for common plugins
def git_checkout(
    url: str, branch: str = "main", credentials_id: str | None = None
) -> GitCheckout:
    """Create Git checkout configuration."""
    return GitCheckout(url=url, branch=branch, credentials_id=credentials_id)


def docker_run(image: str, command: str, args: str | None = None) -> str:
    """Create Docker run step."""
    docker = DockerPlugin(image=image, args=args)
    return docker.to_step(command)


def slack_notify(channel: str, message: str, color: str | None = None) -> str:
    """Create Slack notification step."""
    slack = SlackNotification(channel=channel, message=message, color=color)
    return slack.to_step()


def email_notify(to: str, subject: str, body: str) -> str:
    """Create email notification step."""
    email = EmailNotification(to=to, subject=subject, body=body)
    return email.to_step()


def archive_artifacts(artifacts: str, allow_empty: bool = False) -> str:
    """Create artifact archiver step."""
    archiver = ArtifactArchiver(artifacts=artifacts, allow_empty=allow_empty)
    return archiver.to_step()


def publish_junit(test_results: str, allow_empty: bool = False) -> str:
    """Create JUnit publisher step."""
    junit = JUnitPublisher(test_results=test_results, allow_empty=allow_empty)
    return junit.to_step()
