"""AI-powered completion analysis for thought entities."""

import re
import subprocess
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from .config import Config
from .thought_entity import ThoughtEntity


class CompletionAnalysisEngine:
    """Analyzes thought entities to detect completion status."""
    
    def __init__(self, config: Config):
        self.config = config
        
    def analyze_completion(self, entity: ThoughtEntity) -> Dict[str, Any]:
        """Comprehensively analyze if a thought entity is complete."""
        analysis = {
            'entity_path': str(entity.path),
            'current_status': entity.lifecycle_state,
            'completion_confidence': 0.0,
            'evidence': [],
            'recommendations': [],
        }
        
        # Analyze based on entity type
        if entity.type == 'plan':
            analysis = self._analyze_plan_completion(entity, analysis)
        elif entity.type == 'research':
            analysis = self._analyze_research_completion(entity, analysis)
        else:
            analysis = self._analyze_generic_completion(entity, analysis)
            
        # Calculate overall confidence
        analysis['completion_confidence'] = self._calculate_confidence(analysis['evidence'])
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _analyze_plan_completion(self, entity: ThoughtEntity, analysis: Dict) -> Dict:
        """Analyze completion specific to implementation plans."""
        content = entity.content.lower()
        
        # Check for success criteria checkboxes
        checkbox_evidence = self._analyze_checkboxes(entity.content)
        if checkbox_evidence:
            analysis['evidence'].append(checkbox_evidence)
            
        # Check for implementation commits
        git_evidence = self._analyze_git_implementation(entity)
        if git_evidence:
            analysis['evidence'].append(git_evidence)
            
        # Check for artifact creation
        artifact_evidence = self._analyze_created_artifacts(entity)
        if artifact_evidence:
            analysis['evidence'].append(artifact_evidence)
            
        # Check for explicit completion statements
        completion_phrases = [
            'implementation complete', 'successfully implemented', 
            'plan executed', 'all phases complete'
        ]
        
        for phrase in completion_phrases:
            if phrase in content:
                analysis['evidence'].append({
                    'type': 'explicit_completion',
                    'confidence': 0.8,
                    'description': f"Found completion statement: '{phrase}'"
                })
                
        return analysis
    
    def _analyze_research_completion(self, entity: ThoughtEntity, analysis: Dict) -> Dict:
        """Analyze completion specific to research documents."""
        content = entity.content.lower()
        
        # Check for research conclusions
        conclusion_indicators = [
            'conclusion', 'findings', 'summary', 'results', 'outcome'
        ]
        
        for indicator in conclusion_indicators:
            if indicator in content:
                # Look for substantial content after conclusion indicators
                pattern = rf'{indicator}[:\s]+([\s\S]{{50,}})'
                match = re.search(pattern, content)
                if match:
                    analysis['evidence'].append({
                        'type': 'research_conclusion',
                        'confidence': 0.7,
                        'description': f"Found {indicator} section with substantial content"
                    })
                    break
        
        # Check for recommendations or next steps
        if 'recommendation' in content or 'next step' in content:
            analysis['evidence'].append({
                'type': 'actionable_outcome',
                'confidence': 0.6,
                'description': "Found recommendations or next steps"
            })
        
        return analysis
    
    def _analyze_generic_completion(self, entity: ThoughtEntity, analysis: Dict) -> Dict:
        """Generic completion analysis for any thought type."""
        content = entity.content.lower()
        
        # Check for explicit done statements
        done_phrases = [
            'completed', 'finished', 'done', 'resolved', 'implemented'
        ]
        
        for phrase in done_phrases:
            if phrase in content:
                analysis['evidence'].append({
                    'type': 'completion_statement',
                    'confidence': 0.5,
                    'description': f"Found completion indicator: '{phrase}'"
                })
                break
        
        return analysis
        
    def _analyze_checkboxes(self, content: str) -> Optional[Dict]:
        """Analyze success criteria checkboxes in content."""
        # Find all checkboxes
        total_boxes = len(re.findall(r'- \[[ x]\]', content))
        checked_boxes = len(re.findall(r'- \[x\]', content, re.IGNORECASE))
        
        if total_boxes == 0:
            return None
            
        completion_ratio = checked_boxes / total_boxes
        
        return {
            'type': 'checkbox_completion',
            'confidence': completion_ratio,
            'description': f"{checked_boxes}/{total_boxes} success criteria completed ({completion_ratio:.1%})",
            'details': {
                'total_checkboxes': total_boxes,
                'completed_checkboxes': checked_boxes,
                'completion_ratio': completion_ratio
            }
        }
    
    def _analyze_git_implementation(self, entity: ThoughtEntity) -> Optional[Dict]:
        """Analyze git commits for implementation evidence."""
        try:
            # Get topic/title for commit search
            topic = entity.metadata.get('topic', entity.path.stem)
            
            # Search for commits mentioning the topic
            search_terms = self._extract_search_terms(topic)
            
            related_commits = []
            for term in search_terms:
                # Search git log for commits mentioning this term
                try:
                    result = subprocess.run([
                        'git', 'log', '--oneline', '--grep', term, '--since=30 days ago'
                    ], capture_output=True, text=True, cwd=self.config.workspace_dir)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        commits = result.stdout.strip().split('\n')
                        related_commits.extend(commits)
                        
                except subprocess.SubprocessError:
                    continue
                    
            if related_commits:
                return {
                    'type': 'git_implementation',
                    'confidence': min(0.7, len(related_commits) * 0.2),  # Cap at 0.7
                    'description': f"Found {len(related_commits)} related commits",
                    'details': {
                        'related_commits': related_commits[:5],  # Show first 5
                        'total_commits': len(related_commits)
                    }
                }
                
        except Exception:
            pass  # Git analysis failed, continue without it
            
        return None
    
    def _analyze_created_artifacts(self, entity: ThoughtEntity) -> Optional[Dict]:
        """Analyze if artifacts mentioned in the plan have been created."""
        content = entity.content
        
        # Look for file references in the content
        file_patterns = [
            r'`([^`]+\.(py|js|ts|md|json|yaml|yml|txt))`',  # Files in backticks
            r'"([^"]+\.(py|js|ts|md|json|yaml|yml|txt))"',  # Files in quotes
            r'([A-Za-z0-9/_.-]+\.(py|js|ts|md|json|yaml|yml|txt))',  # File patterns
        ]
        
        mentioned_files = set()
        for pattern in file_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    mentioned_files.add(match[0])
                else:
                    mentioned_files.add(match)
        
        if not mentioned_files:
            return None
        
        # Check if mentioned files exist
        existing_files = []
        workspace_dir = self.config.workspace_dir
        
        for file_ref in mentioned_files:
            # Try various interpretations of the file path
            possible_paths = [
                workspace_dir / file_ref,
                workspace_dir / Path(file_ref).name,  # Just filename
                entity.path.parent / file_ref,  # Relative to thought file
            ]
            
            for possible_path in possible_paths:
                if possible_path.exists() and possible_path.is_file():
                    existing_files.append(str(possible_path.relative_to(workspace_dir)))
                    break
        
        if existing_files:
            existence_ratio = len(existing_files) / len(mentioned_files)
            return {
                'type': 'artifact_creation',
                'confidence': existence_ratio * 0.8,  # Scale down slightly
                'description': f"{len(existing_files)}/{len(mentioned_files)} mentioned files exist",
                'details': {
                    'mentioned_files': list(mentioned_files),
                    'existing_files': existing_files,
                    'existence_ratio': existence_ratio
                }
            }
        
        return None
        
    def _extract_search_terms(self, topic: str) -> List[str]:
        """Extract searchable terms from topic/title."""
        # Simple extraction - split on common separators and take meaningful words
        
        # Remove punctuation and split
        cleaned = topic.translate(str.maketrans('', '', string.punctuation))
        words = cleaned.split()
        
        # Filter out common words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        meaningful_words = [w for w in words if len(w) > 3 and w.lower() not in stop_words]
        
        # Also include the original topic for exact matches
        return meaningful_words + [topic]
    
    def _calculate_confidence(self, evidence: List[Dict]) -> float:
        """Calculate overall completion confidence from evidence."""
        if not evidence:
            return 0.0
            
        # Weight different types of evidence
        weights = {
            'checkbox_completion': 1.0,
            'explicit_completion': 0.8,
            'git_implementation': 0.6,
            'artifact_creation': 0.7,
            'research_conclusion': 0.8,
            'actionable_outcome': 0.6,
            'completion_statement': 0.5,
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for item in evidence:
            weight = weights.get(item['type'], 0.5)
            weighted_sum += item['confidence'] * weight
            total_weight += weight
            
        return min(1.0, weighted_sum / total_weight if total_weight > 0 else 0.0)
        
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate action recommendations based on analysis."""
        confidence = analysis['completion_confidence']
        current_status = analysis['current_status']
        recommendations = []
        
        if confidence >= 0.8 and current_status != 'completed':
            recommendations.append("High confidence completion detected - consider marking as completed")
            recommendations.append("Run 'mem8 update-status completed' to update status")
            
        elif confidence >= 0.6:
            recommendations.append("Substantial progress detected - review for potential completion")
            recommendations.append("Check remaining success criteria manually")
            
        elif confidence < 0.3 and current_status == 'completed':
            recommendations.append("Status marked complete but little evidence found - review status")
            
        if not any(e['type'] == 'checkbox_completion' for e in analysis['evidence']):
            recommendations.append("No success criteria checkboxes found - consider adding them")
            
        return recommendations
    
    def analyze_batch(self, entities: List[ThoughtEntity]) -> Dict[str, Any]:
        """Analyze multiple entities and provide batch insights."""
        results = []
        
        for entity in entities:
            analysis = self.analyze_completion(entity)
            results.append(analysis)
        
        # Aggregate insights
        high_confidence_complete = [r for r in results if r['completion_confidence'] >= 0.8]
        potentially_stale = [r for r in results if r['current_status'] == 'completed' and r['completion_confidence'] < 0.3]
        needs_review = [r for r in results if 0.6 <= r['completion_confidence'] < 0.8]
        
        return {
            'total_analyzed': len(results),
            'individual_results': results,
            'batch_insights': {
                'high_confidence_complete': {
                    'count': len(high_confidence_complete),
                    'paths': [r['entity_path'] for r in high_confidence_complete]
                },
                'potentially_stale': {
                    'count': len(potentially_stale),
                    'paths': [r['entity_path'] for r in potentially_stale]
                },
                'needs_review': {
                    'count': len(needs_review),
                    'paths': [r['entity_path'] for r in needs_review]
                }
            }
        }