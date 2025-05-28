from .models import Relation, Alternative, RelationshipType


def create_relations_from_ratings(project_id):
    """
    Automatically create relations between alternatives based on their ratings.
    Higher rating means domination over lower rating.
    """
    # First, delete all existing relations for this project
    Relation.objects.filter(source__project_id=project_id).delete()

    # Get all alternatives ordered by rating (higher rating first)
    alternatives = Alternative.objects.filter(
        project_id=project_id
    ).order_by('-rating')

    # Create relations for each pair of alternatives
    for i, alt1 in enumerate(alternatives):
        for alt2 in alternatives[i+1:]:
            # Since alternatives are ordered by rating (descending),
            # alt1 always has higher or equal rating compared to alt2
            if alt1.rating > alt2.rating:
                Relation.objects.create(
                    source=alt1,
                    target=alt2,
                    relation_type='domination'
                )
            else:  # ratings are equal
                Relation.objects.create(
                    source=alt1,
                    target=alt2,
                    relation_type='indifference'
                )


def analyze_project(project_id):
    """
    Analyze a project's alternatives using graph theory.
    Returns the best alternative based on ratings and relationships.
    """
    # Get all alternatives ordered by rating
    alternatives = Alternative.objects.filter(
        project_id=project_id
    ).order_by('-rating')

    # If there are no alternatives, return None
    if not alternatives.exists():
        return None

    # Create a dictionary to store scores
    scores = {}

    # Calculate scores based on ratings
    total_rating = sum(alt.rating for alt in alternatives)
    for alt in alternatives:
        # Normalize score based on rating
        scores[alt.name] = alt.rating / total_rating if total_rating > 0 else 0

    # Find the best alternative
    best_alternative = max(scores.items(), key=lambda x: x[1])

    return {
        'best_alternative': best_alternative[0],
        'score': best_alternative[1],
        'all_scores': scores
    }


def get_dominance_graph(project_id):
    """
    Create a graph representation of dominance relations.
    Returns nodes and edges for visualization.
    """
    # Get all alternatives and relationship types for the project
    alternatives = Alternative.objects.filter(project_id=project_id)
    relationship_types = RelationshipType.objects.filter(project_id=project_id)

    # Create nodes for alternatives and relationship types
    nodes = []
    # Add alternative nodes
    for alt in alternatives:
        nodes.append({
            'id': alt.name,
            'type': 'alternative',
            'rating': alt.rating
        })
    # Add relationship type nodes
    for rel_type in relationship_types:
        nodes.append({
            'id': rel_type.name,
            'type': 'relationship',
            'description': rel_type.description
        })

    # Get all relations
    relations = Relation.objects.filter(source__project_id=project_id)
    edges = []

    # Add edges between alternatives
    for rel in relations:
        edges.append({
            'source': rel.source.name,
            'target': rel.target.name,
            'type': rel.relation_type,
            'weight': 1.0 if rel.relation_type == 'domination' else 0.5
        })

    # Add edges between alternatives and their relationship types
    for alt in alternatives:
        if alt.relationship:
            edges.append({
                'source': alt.name,
                'target': alt.relationship.name,
                'type': 'has_relationship',
                'weight': 1.0
            })

    return {
        'nodes': nodes,
        'edges': edges
    } 