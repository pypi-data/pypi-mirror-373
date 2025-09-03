import markdown2
from mammoth_commons.datasets import Text
from mammoth_commons.integration import metric
from mammoth_commons.models import LLM
from mammoth_commons.exports import HTML


@metric(
    namespace="mammotheu",
    version="v0048",
    python="3.13",
    packages=(),
)
def llm_audit(
    dataset: Text, model: LLM, sensitive: list[str], chain_of_votes: int = 10
) -> HTML:
    """
    This assessment methodology sets an LLM at the role of fairness auditory and asks it to provide
    a sequence of votes, obtaining an assessment of whether given text is biased or neutral.
    Then, it follows a chain-of-thought approach for summarizing the reasoning associated with all
    valid votes (some votes may be invalid due to erroneous formatting) and eventually identifying
    actionable insights or explanations.

    Args:
        chain_of_votes: How many votes should be casted.
    """
    from mammoth_commons.externals import notify_progress, notify_end

    if isinstance(sensitive, str):
        sensitive = sensitive.split(",")

    commentaries = list()
    sentiment = 0
    chain_of_votes = int(chain_of_votes)
    assert chain_of_votes >= 1, "At least one chained vote is required"

    for i in range(chain_of_votes):
        notify_progress(
            i / (chain_of_votes + 2.0),
            f"Retrieving bias vote and its reasoning: {i+1}/{chain_of_votes}",
        )
        commentary = model.prompt(
            context=f'You are a fairness auditor that aims to uncover biases in the next user statement. Do you consider the user statement biased, and if so why? Start your reply with "Yes." or "No."L. Consider at least the following attributes as sensitive, and examine those separately: {sensitive}',
            prompt=dataset.text,
        )
        if commentary.startswith("Yes."):
            sentiment += 1
            commentary = commentary[4:]
            commentaries.append(commentary)
        elif commentary.startswith("No."):
            commentary = commentary[3:]
            commentaries.append(commentary)
    title = "Neutral text" if sentiment < chain_of_votes * 0.5 else "Biased text"
    notify_progress(
        (chain_of_votes) / (chain_of_votes + 2.0),
        "Aggregating opinions",
    )
    commentary = model.prompt(
        context=f"You are a fairness auditor that needs to summarize in 250 words the following commentaries to declare a text as {title}. Do not acknowledge the existence of intermediate commentaries and do not make any bullet points.",
        prompt=str(commentaries),
    )
    notify_progress(
        (chain_of_votes + 1) / (chain_of_votes + 2.0),
        "Suggesting insights",
    )
    result = model.prompt(
        context=f"You are a fairness auditor that consider the following user input as {title}. The reasoning is provided by the user. Please provide one list of bullet points for {'addressing' if title.startswith('Biased') else 'explaining'} the reasoning as a markdown list. Consider at least the following attributes as sensitive: {sensitive}",
        prompt="Input:" + dataset.text + "\n" + str(commentary),
    )
    notify_end()
    # Bootstrap styled HTML output
    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Text analysis</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body class="bg-light">
            <div class="container py-5">
                <h1 class="mb-4">{title}</h1>

                <div class="card mb-4">
                    <div class="card-header bg-primary text-white">Original text</div>
                    <div class="card-body">
                        <p>{dataset.text}</p>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header bg-warning text-dark">Verdict</div>
                    <div class="card-body">
                        <p class="mb-0"><strong>{title}</strong></p>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header bg-info text-white">Reasoning</div>
                    <div class="card-body">
                        {markdown2.markdown(commentary)}
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header bg-success text-white">{
    'Action points' if title.startswith('Biased') else 'Explanation'
    }</div>
                    <div class="card-body">
                        {markdown2.markdown(result)}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    return HTML(html)
