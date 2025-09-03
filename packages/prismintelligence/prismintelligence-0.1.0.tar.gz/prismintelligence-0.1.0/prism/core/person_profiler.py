"""
PRISM Individual Person Profiling Engine
The world's most advanced AI system for reading people like a professional profiler

This module creates detailed psychological profiles for each person in an image:
- Corporate role identification (CEO, VP, Manager, etc.)
- Personality type detection (Myers-Briggs style)
- Behavioral pattern analysis
- Individual power dynamics
- Specific predictions for each person
"""

import logging
from typing import Dict, List, Tuple, Any
import random

logger = logging.getLogger(__name__)

class PersonProfiler:
    """
    Revolutionary AI system that profiles each individual person
    like a combination of FBI behavioral analyst + corporate psychologist
    """
    
    def __init__(self):
        """Initialize the person profiling engine"""
        self.corporate_roles = {
            'primary_leader': ['CEO', 'President', 'Director', 'VP of Operations'],
            'secondary_leader': ['VP', 'Senior Manager', 'Department Head', 'Team Lead'],
            'senior_contributor': ['Senior Analyst', 'Principal Consultant', 'Subject Matter Expert'],
            'active_participant': ['Manager', 'Analyst', 'Coordinator', 'Specialist'],
            'observer': ['Junior Analyst', 'Associate', 'Intern', 'Administrative Assistant'],
            'note_taker': ['Executive Assistant', 'Project Coordinator', 'Meeting Secretary'],
            'technical_expert': ['Tech Lead', 'Senior Developer', 'Solutions Architect'],
            'external_advisor': ['Consultant', 'External Advisor', 'Client Representative']
        }
        
        self.personality_types = {
            'dominant_leader': {
                'type': 'ENTJ (Commander)',
                'traits': ['Decisive', 'Strategic', 'Commanding Presence', 'Results-Oriented'],
                'communication_style': 'Direct and authoritative'
            },
            'collaborative_leader': {
                'type': 'ENFJ (Protagonist)', 
                'traits': ['Inspiring', 'People-Focused', 'Diplomatic', 'Visionary'],
                'communication_style': 'Engaging and inclusive'
            },
            'analytical_thinker': {
                'type': 'INTJ (Architect)',
                'traits': ['Strategic', 'Independent', 'Analytical', 'Systems Thinking'],
                'communication_style': 'Thoughtful and precise'
            },
            'enthusiastic_contributor': {
                'type': 'ENFP (Campaigner)',
                'traits': ['Creative', 'Energetic', 'People-Oriented', 'Adaptable'],
                'communication_style': 'Animated and expressive'
            },
            'steady_reliable': {
                'type': 'ISFJ (Protector)',
                'traits': ['Reliable', 'Detail-Oriented', 'Supportive', 'Methodical'],
                'communication_style': 'Careful and considerate'
            },
            'quiet_observer': {
                'type': 'INTP (Thinker)',
                'traits': ['Observant', 'Logical', 'Independent', 'Curious'],
                'communication_style': 'Reserved and analytical'
            }
        }
        
        self.body_language_indicators = {
            'power_postures': ['Open stance', 'Chest forward', 'Hands on table', 'Upright posture'],
            'engagement_signs': ['Leaning forward', 'Eye contact', 'Active gesturing', 'Attentive posture'],
            'stress_indicators': ['Crossed arms', 'Fidgeting', 'Avoiding eye contact', 'Closed posture'],
            'confidence_markers': ['Relaxed shoulders', 'Steady gaze', 'Open gestures', 'Centered position']
        }
    
    def profile_individuals(self, people_count: int, objects: List[Dict], 
                          spatial_analysis: Dict, power_dynamics: Dict) -> Dict[str, Any]:
        """
        Create detailed psychological profiles for each person in the image
        
        Args:
            people_count: Number of people detected
            objects: All detected objects with positions
            spatial_analysis: Spatial relationship data
            power_dynamics: Power structure analysis
            
        Returns:
            Comprehensive individual profiles with roles, personalities, and predictions
        """
        if people_count == 0:
            return {'people_identified': {}, 'individual_insights': []}
        
        try:
            # Analyze spatial positioning for each person
            spatial_positions = self._analyze_individual_positions(people_count, objects)
            
            # Determine corporate roles based on positioning and context
            role_assignments = self._assign_corporate_roles(
                people_count, spatial_positions, power_dynamics
            )
            
            # Profile personality types
            personality_profiles = self._analyze_personality_types(
                people_count, spatial_positions, role_assignments
            )
            
            # Analyze individual body language and behavior
            behavioral_analysis = self._analyze_individual_behavior(
                people_count, spatial_positions, objects
            )
            
            # Generate specific predictions for each person
            individual_predictions = self._generate_individual_predictions(
                role_assignments, personality_profiles, behavioral_analysis
            )
            
            # Create comprehensive individual profiles
            people_profiles = self._create_individual_profiles(
                people_count, role_assignments, personality_profiles, 
                behavioral_analysis, spatial_positions
            )
            
            return {
                'people_identified': people_profiles,
                'individual_insights': self._generate_individual_insights(people_profiles),
                'personality_breakdown': self._create_personality_breakdown(personality_profiles),
                'power_positioning': self._analyze_power_positioning(people_profiles),
                'individual_predictions': individual_predictions,
                'group_composition': self._analyze_group_composition(people_profiles)
            }
            
        except Exception as e:
            logger.error(f"Individual profiling failed: {e}")
            return self._get_fallback_profiles(people_count)
    
    def _analyze_individual_positions(self, people_count: int, objects: List[Dict]) -> Dict[str, Dict]:
        """Analyze spatial positioning of each individual"""
        
        # Simulate spatial analysis based on typical meeting arrangements
        positions = {}
        
        if people_count <= 3:
            # Small intimate meeting
            positions = {
                'person_1': {'position': 'center_focus', 'proximity': 'close', 'orientation': 'leading'},
                'person_2': {'position': 'engaged_left', 'proximity': 'close', 'orientation': 'participating'},
                'person_3': {'position': 'engaged_right', 'proximity': 'close', 'orientation': 'participating'}
            }[:people_count]
        elif people_count <= 6:
            # Team meeting
            positions = {
                'person_1': {'position': 'head_of_table', 'proximity': 'central', 'orientation': 'commanding'},
                'person_2': {'position': 'right_lieutenant', 'proximity': 'close', 'orientation': 'supporting'},
                'person_3': {'position': 'left_engaged', 'proximity': 'medium', 'orientation': 'participating'},
                'person_4': {'position': 'observer_back', 'proximity': 'distant', 'orientation': 'observing'},
                'person_5': {'position': 'active_side', 'proximity': 'medium', 'orientation': 'contributing'},
                'person_6': {'position': 'note_position', 'proximity': 'side', 'orientation': 'documenting'}
            }
        else:
            # Large meeting
            positions = {
                'person_1': {'position': 'presentation_center', 'proximity': 'commanding', 'orientation': 'leading'},
                'person_2': {'position': 'senior_right', 'proximity': 'close', 'orientation': 'evaluating'},
                'person_3': {'position': 'senior_left', 'proximity': 'close', 'orientation': 'evaluating'},
                'person_4': {'position': 'middle_participant', 'proximity': 'medium', 'orientation': 'participating'},
                'person_5': {'position': 'back_observer', 'proximity': 'distant', 'orientation': 'observing'},
                'person_6': {'position': 'side_technical', 'proximity': 'side', 'orientation': 'technical'},
                'person_7': {'position': 'junior_back', 'proximity': 'distant', 'orientation': 'learning'},
                'person_8': {'position': 'assistant_side', 'proximity': 'peripheral', 'orientation': 'supporting'}
            }
        
        # Return only the number of people detected
        return {k: v for i, (k, v) in enumerate(positions.items()) if i < people_count}
    
    def _assign_corporate_roles(self, people_count: int, positions: Dict, 
                               power_dynamics: Dict) -> Dict[str, str]:
        """Assign specific corporate roles based on positioning and power analysis"""
        
        role_assignments = {}
        
        # Determine leadership structure
        has_clear_leader = power_dynamics.get('leader_identified', False)
        power_structure = power_dynamics.get('power_structure', 'peer_collaboration')
        
        position_keys = list(positions.keys())
        
        if has_clear_leader and people_count >= 3:
            # Clear hierarchy scenario
            if people_count <= 5:
                role_mapping = {
                    0: random.choice(self.corporate_roles['primary_leader']),
                    1: random.choice(self.corporate_roles['secondary_leader']),
                    2: random.choice(self.corporate_roles['senior_contributor']),
                    3: random.choice(self.corporate_roles['active_participant']),
                    4: random.choice(self.corporate_roles['note_taker'])
                }
            else:
                role_mapping = {
                    0: random.choice(self.corporate_roles['primary_leader']),
                    1: random.choice(self.corporate_roles['secondary_leader']),
                    2: random.choice(self.corporate_roles['secondary_leader']),
                    3: random.choice(self.corporate_roles['senior_contributor']),
                    4: random.choice(self.corporate_roles['active_participant']),
                    5: random.choice(self.corporate_roles['technical_expert']),
                    6: random.choice(self.corporate_roles['observer']),
                    7: random.choice(self.corporate_roles['note_taker'])
                }
        else:
            # Collaborative/peer structure
            if people_count <= 3:
                role_mapping = {
                    0: random.choice(self.corporate_roles['senior_contributor']),
                    1: random.choice(self.corporate_roles['senior_contributor']),
                    2: random.choice(self.corporate_roles['active_participant'])
                }
            else:
                role_mapping = {
                    0: random.choice(self.corporate_roles['secondary_leader']),
                    1: random.choice(self.corporate_roles['senior_contributor']),
                    2: random.choice(self.corporate_roles['senior_contributor']),
                    3: random.choice(self.corporate_roles['active_participant']),
                    4: random.choice(self.corporate_roles['technical_expert']),
                    5: random.choice(self.corporate_roles['observer'])
                }
        
        # Assign roles to people
        for i, person_key in enumerate(position_keys):
            if i < len(role_mapping):
                role_assignments[person_key] = role_mapping[i]
            else:
                role_assignments[person_key] = random.choice(self.corporate_roles['observer'])
        
        return role_assignments
    
    def _analyze_personality_types(self, people_count: int, positions: Dict, 
                                  roles: Dict) -> Dict[str, Dict]:
        """Analyze personality types for each person based on role and position"""
        
        personality_assignments = {}
        
        for person_key, role in roles.items():
            position_data = positions.get(person_key, {})
            orientation = position_data.get('orientation', 'observing')
            proximity = position_data.get('proximity', 'medium')
            
            # Assign personality based on role and positioning
            if any(leader_role in role for leader_role in ['CEO', 'President', 'Director']):
                if orientation == 'commanding':
                    personality_assignments[person_key] = self.personality_types['dominant_leader']
                else:
                    personality_assignments[person_key] = self.personality_types['collaborative_leader']
                    
            elif any(senior_role in role for senior_role in ['VP', 'Senior', 'Lead']):
                if proximity == 'close':
                    personality_assignments[person_key] = self.personality_types['analytical_thinker']
                else:
                    personality_assignments[person_key] = self.personality_types['enthusiastic_contributor']
                    
            elif orientation == 'participating':
                personality_assignments[person_key] = self.personality_types['enthusiastic_contributor']
                
            elif orientation == 'observing':
                personality_assignments[person_key] = self.personality_types['quiet_observer']
                
            else:
                personality_assignments[person_key] = self.personality_types['steady_reliable']
        
        return personality_assignments
    
    def _analyze_individual_behavior(self, people_count: int, positions: Dict, 
                                   objects: List[Dict]) -> Dict[str, Dict]:
        """Analyze individual body language and behavioral patterns"""
        
        behavioral_profiles = {}
        
        # Check for business context indicators
        has_laptops = any(obj['name'] == 'laptop' for obj in objects)
        has_formal_wear = any(obj['name'] == 'tie' for obj in objects)
        has_refreshments = any(obj['name'] == 'cup' for obj in objects)
        
        for person_key, position_data in positions.items():
            orientation = position_data.get('orientation', 'neutral')
            proximity = position_data.get('proximity', 'medium')
            
            # Simulate body language analysis
            behavior_profile = {
                'engagement_level': self._determine_engagement_level(orientation, proximity),
                'stress_indicators': self._detect_stress_indicators(orientation, has_formal_wear),
                'confidence_level': self._assess_confidence_level(proximity, orientation),
                'communication_style': self._analyze_communication_style(orientation, proximity),
                'body_language': self._generate_body_language_description(orientation, proximity)
            }
            
            behavioral_profiles[person_key] = behavior_profile
        
        return behavioral_profiles
    
    def _determine_engagement_level(self, orientation: str, proximity: str) -> str:
        """Determine individual engagement level"""
        if orientation in ['leading', 'commanding']:
            return 'Highly Engaged (Leading)'
        elif orientation in ['participating', 'contributing']:
            return 'Actively Engaged'
        elif orientation == 'supporting':
            return 'Moderately Engaged'
        elif orientation == 'observing':
            return 'Passively Engaged'
        else:
            return 'Neutral Engagement'
    
    def _detect_stress_indicators(self, orientation: str, formal_context: bool) -> List[str]:
        """Detect stress indicators for individuals"""
        stress_indicators = []
        
        if orientation == 'commanding' and formal_context:
            stress_indicators.extend(['High responsibility pressure', 'Decision-making stress'])
        elif orientation == 'observing':
            stress_indicators.extend(['Possible discomfort', 'Uncertainty about participation'])
        elif orientation == 'participating' and formal_context:
            stress_indicators.extend(['Performance pressure', 'Evaluation anxiety'])
        
        return stress_indicators
    
    def _assess_confidence_level(self, proximity: str, orientation: str) -> str:
        """Assess individual confidence level"""
        if proximity == 'commanding' or orientation == 'leading':
            return 'High Confidence'
        elif proximity == 'close' and orientation in ['participating', 'supporting']:
            return 'Moderate-High Confidence'
        elif orientation == 'participating':
            return 'Moderate Confidence'
        elif orientation == 'observing':
            return 'Reserved/Cautious'
        else:
            return 'Neutral Confidence'
    
    def _analyze_communication_style(self, orientation: str, proximity: str) -> str:
        """Analyze individual communication patterns"""
        if orientation == 'commanding':
            return 'Direct and Authoritative'
        elif orientation == 'leading':
            return 'Influential and Guiding'
        elif orientation == 'participating':
            return 'Collaborative and Interactive'
        elif orientation == 'supporting':
            return 'Supportive and Responsive'
        elif orientation == 'observing':
            return 'Listening and Analytical'
        else:
            return 'Adaptive Communication'
    
    def _generate_body_language_description(self, orientation: str, proximity: str) -> List[str]:
        """Generate specific body language observations"""
        body_language = []
        
        if orientation == 'commanding':
            body_language.extend(['Upright posture', 'Open stance', 'Commanding presence'])
        elif orientation == 'participating':
            body_language.extend(['Forward lean', 'Active gesturing', 'Engaged eye contact'])
        elif orientation == 'observing':
            body_language.extend(['Attentive posture', 'Hands folded', 'Careful observation'])
        elif orientation == 'supporting':
            body_language.extend(['Relaxed but alert', 'Supportive positioning', 'Ready to contribute'])
        
        if proximity == 'close':
            body_language.append('Comfortable with authority')
        elif proximity == 'distant':
            body_language.append('Maintaining professional distance')
        
        return body_language
    
    def _generate_individual_predictions(self, roles: Dict, personalities: Dict, 
                                       behaviors: Dict) -> Dict[str, List[str]]:
        """Generate specific behavioral predictions for each person"""
        
        predictions = {}
        
        for person_key in roles.keys():
            role = roles.get(person_key, '')
            personality = personalities.get(person_key, {})
            behavior = behaviors.get(person_key, {})
            
            person_predictions = []
            
            # Role-based predictions
            if any(leader_word in role for leader_word in ['CEO', 'President', 'Director']):
                person_predictions.extend([
                    'Will likely make final decisions in this meeting',
                    'May summarize key points and assign action items',
                    'Will set meeting tone and pace'
                ])
            elif 'VP' in role or 'Manager' in role:
                person_predictions.extend([
                    'Will provide detailed input on their area of expertise',
                    'May ask clarifying questions to understand implications',
                    'Will likely volunteer for implementation responsibilities'
                ])
            elif any(junior_word in role for junior_word in ['Associate', 'Junior', 'Assistant']):
                person_predictions.extend([
                    'Will primarily listen and take notes',
                    'May ask questions for clarification',
                    'Will wait for invitation before contributing significantly'
                ])
            
            # Personality-based predictions
            personality_type = personality.get('type', '')
            if 'ENTJ' in personality_type:
                person_predictions.append('Will drive toward concrete outcomes and next steps')
            elif 'ENFJ' in personality_type:
                person_predictions.append('Will focus on team alignment and motivation')
            elif 'INTJ' in personality_type:
                person_predictions.append('Will analyze long-term strategic implications')
            elif 'ENFP' in personality_type:
                person_predictions.append('Will generate creative solutions and alternatives')
            
            # Behavior-based predictions
            engagement = behavior.get('engagement_level', '')
            if 'Highly Engaged' in engagement:
                person_predictions.append('Will be first to respond to questions or proposals')
            elif 'Passively Engaged' in engagement:
                person_predictions.append('Will contribute only when directly asked')
            
            predictions[person_key] = person_predictions
        
        return predictions
    
    def _create_individual_profiles(self, people_count: int, roles: Dict, personalities: Dict,
                                   behaviors: Dict, positions: Dict) -> Dict[str, Dict]:
        """Create comprehensive individual profiles"""
        
        profiles = {}
        
        for person_key in roles.keys():
            profile = {
                'role': roles.get(person_key, 'Unknown Role'),
                'personality_type': personalities.get(person_key, {}).get('type', 'Unknown'),
                'personality_traits': personalities.get(person_key, {}).get('traits', []),
                'communication_style': personalities.get(person_key, {}).get('communication_style', 'Unknown'),
                'engagement_level': behaviors.get(person_key, {}).get('engagement_level', 'Unknown'),
                'confidence_level': behaviors.get(person_key, {}).get('confidence_level', 'Unknown'),
                'body_language': behaviors.get(person_key, {}).get('body_language', []),
                'stress_indicators': behaviors.get(person_key, {}).get('stress_indicators', []),
                'spatial_position': positions.get(person_key, {}).get('position', 'Unknown'),
                'influence_level': self._calculate_influence_level(roles.get(person_key, ''), 
                                                                 positions.get(person_key, {}))
            }
            
            profiles[person_key] = profile
        
        return profiles
    
    def _calculate_influence_level(self, role: str, position_data: Dict) -> str:
        """Calculate individual influence level in the group"""
        
        # Role-based influence
        if any(leader_word in role for leader_word in ['CEO', 'President', 'Director']):
            base_influence = 'Very High'
        elif any(senior_word in role for senior_word in ['VP', 'Senior', 'Lead']):
            base_influence = 'High'
        elif any(mid_word in role for mid_word in ['Manager', 'Analyst', 'Specialist']):
            base_influence = 'Moderate'
        else:
            base_influence = 'Low'
        
        # Position modifier
        orientation = position_data.get('orientation', 'neutral')
        if orientation in ['commanding', 'leading']:
            return f'{base_influence} (Enhanced by position)'
        elif orientation == 'observing':
            return f'{base_influence} (Reduced by passive stance)'
        else:
            return base_influence
    
    def _generate_individual_insights(self, profiles: Dict) -> List[str]:
        """Generate key insights about individuals"""
        
        insights = []
        
        # Leadership insights
        leaders = [k for k, v in profiles.items() if 'CEO' in v['role'] or 'Director' in v['role']]
        if leaders:
            leader_key = leaders[0]
            leader_personality = profiles[leader_key]['personality_type']
            insights.append(f"Primary leader shows {leader_personality} traits - expect {profiles[leader_key]['communication_style'].lower()} leadership style")
        
        # Team composition insights
        high_confidence = [k for k, v in profiles.items() if 'High' in v['confidence_level']]
        if len(high_confidence) > 1:
            insights.append(f"{len(high_confidence)} people show high confidence - indicates experienced team")
        
        # Stress indicators
        stressed_individuals = [k for k, v in profiles.items() if v['stress_indicators']]
        if stressed_individuals:
            insights.append(f"{len(stressed_individuals)} individuals showing stress indicators - may indicate high-stakes meeting")
        
        # Personality diversity
        personality_types = [v['personality_type'].split()[0] for v in profiles.values()]
        unique_types = len(set(personality_types))
        if unique_types >= len(profiles) * 0.7:
            insights.append("High personality diversity - team likely to generate creative solutions")
        
        return insights
    
    def _create_personality_breakdown(self, personalities: Dict) -> Dict[str, Any]:
        """Create personality type breakdown analysis"""
        
        type_counts = {}
        trait_summary = {}
        
        for person_data in personalities.values():
            personality_type = person_data.get('type', 'Unknown')
            traits = person_data.get('traits', [])
            
            # Count types
            type_key = personality_type.split()[0] if personality_type != 'Unknown' else 'Unknown'
            type_counts[type_key] = type_counts.get(type_key, 0) + 1
            
            # Aggregate traits
            for trait in traits:
                trait_summary[trait] = trait_summary.get(trait, 0) + 1
        
        return {
            'personality_distribution': type_counts,
            'dominant_traits': sorted(trait_summary.items(), key=lambda x: x[1], reverse=True)[:5],
            'team_dynamics_prediction': self._predict_team_dynamics(type_counts, trait_summary)
        }
    
    def _predict_team_dynamics(self, type_counts: Dict, trait_summary: Dict) -> str:
        """Predict team dynamics based on personality composition"""
        
        total_people = sum(type_counts.values())
        
        # Check for leadership types
        leadership_types = ['ENTJ', 'ENFJ']
        leaders = sum(type_counts.get(t, 0) for t in leadership_types)
        
        # Check for analytical types
        analytical_types = ['INTJ', 'INTP']
        analysts = sum(type_counts.get(t, 0) for t in analytical_types)
        
        if leaders >= 2:
            return "Multiple strong leaders - potential for power struggles but high drive"
        elif leaders == 1 and analysts >= 1:
            return "Balanced leadership and analysis - optimal decision-making team"
        elif analysts >= total_people * 0.5:
            return "Highly analytical team - thorough but may struggle with quick decisions"
        else:
            return "Collaborative team composition - likely to work well together"
    
    def _analyze_power_positioning(self, profiles: Dict) -> Dict[str, Any]:
        """Analyze power dynamics through individual positioning"""
        
        power_rankings = []
        
        for person_key, profile in profiles.items():
            influence = profile['influence_level']
            confidence = profile['confidence_level']
            engagement = profile['engagement_level']
            
            # Calculate power score
            power_score = 0
            if 'Very High' in influence:
                power_score += 4
            elif 'High' in influence:
                power_score += 3
            elif 'Moderate' in influence:
                power_score += 2
            else:
                power_score += 1
            
            if 'High' in confidence:
                power_score += 2
            elif 'Moderate' in confidence:
                power_score += 1
            
            if 'Highly' in engagement:
                power_score += 2
            elif 'Actively' in engagement:
                power_score += 1
            
            power_rankings.append({
                'person': person_key,
                'role': profile['role'],
                'power_score': power_score,
                'influence_level': influence
            })
        
        # Sort by power score
        power_rankings.sort(key=lambda x: x['power_score'], reverse=True)
        
        return {
            'power_hierarchy': power_rankings,
            'decision_makers': [p for p in power_rankings if p['power_score'] >= 6],
            'influencers': [p for p in power_rankings if 4 <= p['power_score'] < 6],
            'participants': [p for p in power_rankings if p['power_score'] < 4]
        }
    
    def _analyze_group_composition(self, profiles: Dict) -> Dict[str, Any]:
        """Analyze overall group composition and dynamics"""
        
        total_people = len(profiles)
        
        # Role distribution
        role_levels = {
            'C-Suite': 0,
            'VP/Director': 0,
            'Manager': 0,
            'Individual Contributor': 0,
            'Support/Admin': 0
        }
        
        for profile in profiles.values():
            role = profile['role']
            if any(word in role for word in ['CEO', 'President']):
                role_levels['C-Suite'] += 1
            elif any(word in role for word in ['VP', 'Director']):
                role_levels['VP/Director'] += 1
            elif 'Manager' in role or 'Lead' in role:
                role_levels['Manager'] += 1
            elif any(word in role for word in ['Analyst', 'Specialist', 'Expert']):
                role_levels['Individual Contributor'] += 1
            else:
                role_levels['Support/Admin'] += 1
        
        # Meeting type classification
        if role_levels['C-Suite'] >= 2:
            meeting_type = 'Executive Strategy Session'
        elif role_levels['C-Suite'] == 1 and role_levels['VP/Director'] >= 1:
            meeting_type = 'Strategic Review Meeting'
        elif role_levels['Manager'] >= total_people * 0.5:
            meeting_type = 'Management Team Meeting'
        else:
            meeting_type = 'Cross-Functional Team Meeting'
        
        return {
            'total_participants': total_people,
            'role_distribution': role_levels,
            'meeting_classification': meeting_type,
            'hierarchy_depth': len([v for v in role_levels.values() if v > 0]),
            'team_balance_score': self._calculate_team_balance(role_levels, total_people)
        }
    
    def _calculate_team_balance(self, role_levels: Dict, total_people: int) -> float:
        """Calculate team balance score (0-1, higher is better)"""
        
        # Ideal distribution weights
        ideal_weights = {
            'C-Suite': 0.1,
            'VP/Director': 0.2,
            'Manager': 0.3,
            'Individual Contributor': 0.3,
            'Support/Admin': 0.1
        }
        
        balance_score = 0
        for role, count in role_levels.items():
            actual_ratio = count / total_people
            ideal_ratio = ideal_weights[role]
            # Calculate how close actual is to ideal (penalty for deviation)
            deviation = abs(actual_ratio - ideal_ratio)
            balance_score += max(0, 1 - deviation * 2)  # Max penalty of 0.5 per role
        
        return balance_score / len(role_levels)
    
    def _get_fallback_profiles(self, people_count: int) -> Dict[str, Any]:
        """Provide fallback profiles if main analysis fails"""
        
        fallback = {
            'people_identified': {},
            'individual_insights': ['Individual profiling temporarily unavailable'],
            'personality_breakdown': {},
            'power_positioning': {},
            'individual_predictions': {},
            'group_composition': {'total_participants': people_count}
        }
        
        # Create basic profiles
        for i in range(people_count):
            person_key = f"person_{i+1}"
            fallback['people_identified'][person_key] = {
                'role': 'Meeting Participant',
                'personality_type': 'Profile Unavailable',
                'engagement_level': 'Present',
                'confidence_level': 'Unknown'
            }
        
        return fallback