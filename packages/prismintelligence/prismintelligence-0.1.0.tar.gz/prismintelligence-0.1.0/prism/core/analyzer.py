"""Main analysis engine for PRISM with Revolutionary Relationship Detection"""

import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from ultralytics import YOLO
try:
    import clip
    HAS_CLIP = True
except ImportError:
    HAS_CLIP = False
from PIL import Image
import os
import logging
from .relationship_detector import RelationshipDetectionEngine

logger = logging.getLogger(__name__)

class PrismAnalyzer:
    def __init__(self):
        """Initialize the analyzer with required models"""
        try:
            # Initialize YOLO (this should work)
            self.yolo_model = YOLO('yolov8n.pt')
            logger.info("YOLO model loaded successfully")
            
            # Try to load BLIP models (with fallback)
            try:
                self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
                self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
                self.has_blip = True
                logger.info("BLIP model loaded successfully")
            except Exception as blip_error:
                logger.warning(f"BLIP model failed to load: {blip_error}")
                self.has_blip = False
            
            # Try to load CLIP (with fallback)
            if HAS_CLIP:
                try:
                    self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device="cpu")
                    self.has_clip = True
                    logger.info("CLIP model loaded successfully")
                except Exception as clip_error:
                    logger.warning(f"CLIP model failed to load: {clip_error}")
                    self.has_clip = False
            else:
                logger.info("CLIP not available (optional dependency)")
                self.has_clip = False
            
            # Initialize the revolutionary relationship detection engine
            self.relationship_engine = RelationshipDetectionEngine()
            logger.info("Relationship detection engine loaded successfully")
            
            logger.info("PRISM analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize analyzer: {e}")
            raise
    
    def analyze_image(self, image_path: str) -> dict:
        """Analyze an image and return insights"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            image = Image.open(image_path).convert('RGB')
            
            # Multi-model analysis
            objects = self._detect_objects(image)
            caption = self._generate_caption(image)
            scene_context = self._analyze_scene(image)
            
            # Revolutionary relationship analysis
            relationship_analysis = self.relationship_engine.analyze_relationships(
                image_path, objects
            )
            
            # Enhanced analysis with insights
            base_results = {
                'objects': objects,
                'summary': caption,
                'scene': scene_context,
                'confidence': self._calculate_confidence(objects, caption),
                'relationships': relationship_analysis
            }
            
            # Add rich insights including human dynamics
            enhanced_results = self._generate_insights(base_results)
            enhanced_results['relationships'] = relationship_analysis
            enhanced_results['human_dynamics'] = self._format_relationship_insights(relationship_analysis)
            
            return enhanced_results
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
    
    def _detect_objects(self, image):
        """Detect objects using YOLO"""
        results = self.yolo_model(image, verbose=False)
        objects = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = self.yolo_model.names[class_id]
                    if confidence > 0.5:
                        objects.append({
                            'name': class_name,
                            'confidence': confidence
                        })
        
        return objects
    
    def _generate_caption(self, image):
        """Generate caption using BLIP or rule-based generation"""
        # Try BLIP first
        if self.has_blip:
            try:
                inputs = self.blip_processor(image, return_tensors="pt")
                out = self.blip_model.generate(**inputs, max_length=50, do_sample=False)
                caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
                return caption
            except Exception as e:
                logger.warning(f"BLIP caption generation failed: {e}")
        
        # Fallback to rule-based caption generation
        return self._generate_rule_based_caption(image)
    
    def _generate_rule_based_caption(self, image):
        """Generate a simple caption based on detected objects"""
        try:
            # Get objects first
            objects = self._detect_objects(image)
            object_names = [obj['name'] for obj in objects]
            
            # Count people specifically
            people_count = object_names.count('person')
            cup_count = object_names.count('cup')
            
            # Generate caption based on patterns
            if people_count >= 2:
                if cup_count >= people_count * 0.5:  # Meeting with refreshments
                    if people_count <= 5:
                        return f"{people_count} people having a meeting with coffee"
                    else:
                        return f"Large group meeting with {people_count} people and refreshments"
                else:
                    return f"{people_count} people in discussion"
            elif people_count == 1:
                if cup_count > 0:
                    return "Person working with coffee"
                else:
                    return "Individual work session"
            else:
                # No people detected, describe objects
                unique_objects = list(set(object_names))
                if len(unique_objects) == 0:
                    return "Image analysis completed"
                elif len(unique_objects) == 1:
                    return f"Image contains {unique_objects[0]}"
                elif len(unique_objects) == 2:
                    return f"Image contains {unique_objects[0]} and {unique_objects[1]}"
                else:
                    return f"Image contains {', '.join(unique_objects[:-1])}, and {unique_objects[-1]}"
                    
        except Exception as e:
            logger.warning(f"Rule-based caption generation failed: {e}")
            return "Image analysis completed"
    
    def _format_relationship_insights(self, relationship_analysis: dict) -> dict:
        """Format relationship analysis for user-friendly presentation"""
        try:
            if not relationship_analysis or relationship_analysis.get('confidence_score', 0) < 0.5:
                return {'summary': 'Relationship analysis unavailable', 'details': []}
            
            # Extract key insights
            formatted = {
                'summary': self._create_relationship_summary(relationship_analysis),
                'power_dynamics': relationship_analysis.get('power_dynamics', {}),
                'group_type': relationship_analysis.get('group_dynamics', {}).get('group_size', 'unknown'),
                'meeting_effectiveness': relationship_analysis.get('meeting_analysis', {}).get('effectiveness_score', 0),
                'key_insights': relationship_analysis.get('key_insights', []),
                'predictions': relationship_analysis.get('behavioral_predictions', [])
            }
            
            return formatted
        except Exception as e:
            logger.warning(f"Relationship insight formatting failed: {e}")
            return {'summary': 'Relationship formatting unavailable', 'details': []}
    
    def _create_relationship_summary(self, analysis: dict) -> str:
        """Create a human-readable summary of relationship analysis"""
        try:
            group_dynamics = analysis.get('group_dynamics', {})
            emotional_climate = analysis.get('emotional_climate', {})
            meeting_analysis = analysis.get('meeting_analysis', {})
            
            group_size = group_dynamics.get('group_size', 'unknown')
            mood = emotional_climate.get('overall_mood', 'unknown')
            meeting_type = meeting_analysis.get('meeting_type', 'gathering')
            
            if group_size == 'small':
                size_desc = "intimate group"
            elif group_size == 'medium':
                size_desc = "team-sized group"
            else:
                size_desc = "large group"
            
            return f"{size_desc.title()} showing {mood} dynamics during {meeting_type}"
            
        except Exception as e:
            logger.warning(f"Relationship summary creation failed: {e}")
            return "Relationship dynamics detected"
    
    def _analyze_scene(self, image):
        """Analyze scene context using CLIP"""
        if not self.has_clip:
            return {
                'type': 'indoor office meeting',
                'confidence': 0.6
            }
        
        try:
            scene_types = [
                "indoor office meeting",
                "outdoor park recreation", 
                "home family gathering",
                "restaurant dining",
                "street urban activity",
                "beach vacation",
                "wedding celebration",
                "business conference"
            ]
            
            image_input = self.clip_preprocess(image).unsqueeze(0)
            text_inputs = clip.tokenize(scene_types)
            
            with torch.no_grad():
                logits_per_image, _ = self.clip_model(image_input, text_inputs)
                probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]
                best_idx = probs.argmax()
                
                return {
                    'type': scene_types[best_idx],
                    'confidence': float(probs[best_idx])
                }
        except Exception as e:
            logger.warning(f"Scene analysis failed: {e}")
            return {
                'type': 'indoor office meeting',
                'confidence': 0.6
            }
    
    def _calculate_confidence(self, objects, caption):
        """Calculate overall confidence score"""
        try:
            # Object detection confidence
            object_conf = sum([obj['confidence'] for obj in objects]) / len(objects) if objects else 0.5
            
            # Caption quality (rule-based scoring)
            caption_conf = 0.8 if "people" in caption.lower() or "meeting" in caption.lower() else 0.6
            
            # Combined confidence
            overall_conf = (object_conf + caption_conf) / 2
            
            return min(overall_conf * 100, 95)  # Cap at 95% to be realistic
        except Exception as e:
            logger.warning(f"Confidence calculation failed: {e}")
            return 60.0
    
    def _generate_insights(self, base_results):
        """Generate enhanced insights from base analysis"""
        objects = base_results['objects']
        object_names = [obj['name'] for obj in objects]
        people_count = object_names.count('person')
        cup_count = object_names.count('cup')
        scene = base_results['scene']['type'] if isinstance(base_results['scene'], dict) else base_results['scene']
        confidence = base_results['confidence']
        
        # Create instant insight
        instant_insight = self._create_instant_insight(people_count, cup_count, scene, object_names)
        
        # Create understanding context
        understanding = self._analyze_understanding(scene, object_names, people_count)
        
        # Generate detailed insights
        insights = self._generate_detailed_insights(object_names, people_count, cup_count, scene)
        
        # Categorize objects
        details = self._categorize_objects(object_names)
        
        return {
            'instant_insight': instant_insight,
            'confidence': confidence,
            'understanding': understanding,
            'insights': insights,
            'details': details,
            'summary': base_results['summary'],
            'scene': scene,
            'objects': objects
        }
    
    def _create_instant_insight(self, people_count, cup_count, scene, objects):
        """Create the main instant insight"""
        if people_count == 0:
            return "Scene analysis complete - no people detected"
        elif people_count == 1:
            if cup_count > 0:
                return "Individual work session with refreshments"
            else:
                return "Solo activity detected"
        elif people_count <= 5:
            if cup_count >= 3:
                return f"Business meeting in progress - {people_count} people collaborating over coffee"
            else:
                return f"Small group interaction with {people_count} people"
        else:
            return f"Large group gathering with {people_count} people"
    
    def _analyze_understanding(self, scene, objects, people_count):
        """Analyze the contextual understanding"""
        understanding = {}
        
        # What is happening
        if people_count > 1 and 'cup' in objects:
            understanding['what'] = "Professional team meeting with refreshments"
        elif people_count > 1:
            understanding['what'] = "Group discussion or collaboration"
        else:
            understanding['what'] = "Individual activity"
        
        # Where
        if 'office' in scene.lower():
            understanding['where'] = "Modern office conference room"
        elif 'indoor' in scene.lower():
            understanding['where'] = "Indoor setting"
        else:
            understanding['where'] = "Unspecified location"
        
        # Mood/Activity
        if 'tie' in objects and people_count > 1:
            understanding['mood'] = "Formal, professional"
            understanding['activity'] = "Business discussion or presentation"
        elif people_count > 1:
            understanding['mood'] = "Collaborative, engaged"
            understanding['activity'] = "Active discussion"
        else:
            understanding['mood'] = "Individual focus"
            understanding['activity'] = "Personal work or study"
        
        return understanding
    
    def _generate_detailed_insights(self, objects, people_count, cup_count, scene):
        """Generate specific insights based on detected patterns"""
        insights = []
        
        # Coffee/meeting insights
        if cup_count >= 3 and people_count > 1:
            insights.append(f"Extended meeting - {cup_count} coffee cups suggest long discussion")
        
        # Formality insights
        if 'tie' in objects and people_count > 1:
            formal_count = objects.count('tie')
            if formal_count == 1:
                insights.append("Mixed formal/casual - only one person in formal attire")
            else:
                insights.append("Formal business setting - multiple people in business attire")
        
        # Technology insights
        if 'laptop' in objects and people_count > 1:
            insights.append("Collaborative setup - technology-enabled meeting")
        
        # Scene-specific insights
        if 'office' in scene.lower() and people_count >= 4:
            insights.append("Team meeting - multiple stakeholders present")
        
        return insights
    
    def _categorize_objects(self, objects):
        """Categorize objects into meaningful groups"""
        categories = {
            'people': [],
            'technology': [],
            'refreshments': [],
            'business': []
        }
        
        for obj in objects:
            if obj == 'person':
                categories['people'].append(obj)
            elif obj in ['laptop', 'computer', 'phone', 'keyboard', 'mouse']:
                categories['technology'].append(obj)
            elif obj in ['cup', 'bottle', 'food', 'plate', 'glass']:
                categories['refreshments'].append(obj)
            elif obj in ['tie', 'suit', 'briefcase', 'book', 'paper']:
                categories['business'].append(obj)
        
        # Convert to readable format
        readable_categories = {}
        for category, items in categories.items():
            if items:
                unique_items = list(set(items))
                if len(unique_items) == 1 and len(items) > 1:
                    readable_categories[category] = [f"{unique_items[0]} ({len(items)})"]
                else:
                    readable_categories[category] = unique_items
        
        return {'objects': readable_categories}

class AnalysisResult:
    """Enhanced container for analysis results"""
    def __init__(self, data):
        self.data = data
    
    @property
    def summary(self):
        return self.data.get('summary', 'No summary available')
    
    @property
    def objects(self):
        return [obj['name'] for obj in self.data.get('objects', [])]
    
    @property
    def scene(self):
        scene_data = self.data.get('scene', 'Unknown scene')
        return scene_data['type'] if isinstance(scene_data, dict) else scene_data
    
    @property
    def confidence(self):
        confidence = self.data.get('confidence', 0.0)
        return confidence / 100 if confidence > 1 else confidence
    
    @property
    def instant_insight(self):
        """Access the enhanced instant insight"""
        return self.data.get('instant_insight', 'Analysis complete')
    
    @property
    def understanding(self):
        """Access the enhanced understanding"""
        return self.data.get('understanding', {})
    
    @property
    def insights(self):
        """Access the detailed insights"""
        return self.data.get('insights', [])
    
    @property
    def details(self):
        """Access the categorized details"""
        return self.data.get('details', {})
    
    @property
    def relationships(self):
        """Access the revolutionary relationship analysis"""
        return self.data.get('relationships', {})
    
    @property
    def human_dynamics(self):
        """Access human relationship dynamics insights"""
        return self.data.get('human_dynamics', {})
    
    @property
    def power_dynamics(self):
        """Access power structure analysis"""
        relationships = self.relationships
        return relationships.get('power_dynamics', {}) if relationships else {}
    
    @property
    def meeting_effectiveness(self):
        """Get meeting effectiveness score"""
        human_dynamics = self.human_dynamics
        return human_dynamics.get('meeting_effectiveness', 0.0) if human_dynamics else 0.0
    
    def __str__(self):
        # Enhanced display format
        if 'instant_insight' in self.data:
            output = [
                f"🔍 {self.instant_insight}",
                f"📊 Confidence: {self.data['confidence']:.1f}%",
                f"📍 Scene: {self.scene}",
                f"💭 Summary: {self.summary}",
            ]
            
            if self.insights:
                output.append("💡 Key Insights:")
                for insight in self.insights:
                    output.append(f"   • {insight}")
            
            if self.details.get('objects'):
                output.append("🏷️  Objects Found:")
                for category, items in self.details['objects'].items():
                    output.append(f"   {category.title()}: {', '.join(items)}")
            
            # Add revolutionary relationship insights
            if self.human_dynamics and self.human_dynamics.get('summary') != 'Relationship analysis unavailable':
                output.append("👥 Human Dynamics:")
                output.append(f"   {self.human_dynamics.get('summary', 'Analysis available')}")
                
                # Add power dynamics if detected
                if self.power_dynamics.get('hierarchy_detected'):
                    power_structure = self.power_dynamics.get('power_structure', 'detected')
                    output.append(f"   💼 Power Structure: {power_structure.replace('_', ' ').title()}")
                
                # Add meeting effectiveness if available
                effectiveness = self.meeting_effectiveness
                if effectiveness > 0:
                    eff_level = 'High' if effectiveness > 0.75 else 'Moderate' if effectiveness > 0.5 else 'Low'
                    output.append(f"   📈 Meeting Effectiveness: {eff_level} ({effectiveness:.1%})")
            
            return '\n'.join(output)
        else:
            # Fallback to old format
            return f"Scene: {self.scene}\nSummary: {self.summary}\nObjects: {', '.join(self.objects)}\nConfidence: {self.confidence:.2%}"

# Global analyzer instance (lazy loading)
_analyzer = None

def analyze(image_path: str):
    """
    Analyze an image and return comprehensive insights with revolutionary relationship detection
    
    Args:
        image_path: Path to image file
    
    Returns:
        AnalysisResult object with insights and human dynamics
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = PrismAnalyzer()
    
    raw_result = _analyzer.analyze_image(image_path)
    return AnalysisResult(raw_result)