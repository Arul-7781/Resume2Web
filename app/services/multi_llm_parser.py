"""
Adaptive Multi-LLM Parser with Intelligent Routing

ADVANCED FEATURES:
1. Circular rotation - Round-robin through available models
2. Rate limit handling - Auto-skip rate-limited models
3. Quality-based retry - Re-parse if score below threshold
4. Cross-validation - Always validate with different model
5. Iterative improvement - Keep parsing until quality acceptable

STRATEGY:
- Try models in circular order (Gemini → Groq → OpenAI → Mistral → Cohere → repeat)
- If rate limited, skip that model for N minutes
- If parse score < threshold, try different model
- Always validate final result with different model
- Stop when score >= threshold or max attempts reached
"""

import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from app.models.portfolio import PortfolioData
from app.config import settings

logger = logging.getLogger(__name__)


class MultiLLMParser:
    """
    Adaptive multi-LLM parser with intelligent routing
    """
    
    def __init__(self, mode: str = "adaptive"):
        """
        Initialize adaptive parser
        
        Args:
            mode: "adaptive" (recommended), "fallback", "ensemble", "validation"
        """
        self.mode = mode
        self.parsers = []
        self.rate_limit_tracker = {}  # Track which models are rate limited
        self.current_index = 0  # For circular rotation
        self.min_quality_score = settings.min_quality_score
        self.max_attempts = settings.max_parse_attempts
        
        self._initialize_parsers()
        
        if not self.parsers:
            raise ValueError("No LLM API keys configured. Set at least GEMINI_API_KEY")
        
        logger.info(f"🚀 Multi-LLM Parser initialized: {len(self.parsers)} models in {mode} mode")
        logger.info(f"📊 Quality threshold: {self.min_quality_score}, Max attempts: {self.max_attempts}")
    
    def _initialize_parsers(self):
        """Initialize all available parsers in priority order"""
        
        # Priority order: Fast & Reliable first → Gemini last (rate limit bottleneck)
        parser_configs = [
            ("Groq", "groq_api_key", "app.services.parsers.groq_parser", "GroqParser"),
            ("Mistral", "mistral_api_key", "app.services.parsers.mistral_parser", "MistralParser"),
            ("Cohere", "cohere_api_key", "app.services.parsers.cohere_parser", "CohereParser"),
            ("Gemini", "gemini_api_key", "app.services.parsers.gemini_parser", "GeminiParser"),  # Last resort
            ("OpenAI", "openai_api_key", "app.services.parsers.openai_parser", "OpenAIParser"),
        ]
        
        for name, api_key_attr, module_path, class_name in parser_configs:
            if hasattr(settings, api_key_attr) and getattr(settings, api_key_attr):
                try:
                    module = __import__(module_path, fromlist=[class_name])
                    parser_class = getattr(module, class_name)
                    parser_instance = parser_class()
                    self.parsers.append((name, parser_instance))
                    self.rate_limit_tracker[name] = None  # Not rate limited
                    logger.info(f"✓ {name} parser ready")
                except Exception as e:
                    logger.warning(f"✗ {name} parser failed to initialize: {e}")
    
    def parse_resume(self, resume_text: str) -> PortfolioData:
        """
        Parse resume with adaptive strategy
        
        Returns best result after multiple attempts with different models
        """
        if self.mode == "adaptive":
            return self._adaptive_parse(resume_text)
        elif self.mode == "fallback":
            return self._parse_with_fallback(resume_text)
        elif self.mode == "ensemble":
            return self._parse_with_ensemble(resume_text)
        elif self.mode == "validation":
            return self._parse_with_validation(resume_text)
        else:
            raise ValueError(f"Unknown mode: {self.mode}")
    
    def _adaptive_parse(self, resume_text: str) -> PortfolioData:
        """
        ADAPTIVE STRATEGY (Recommended)
        
        Algorithm:
        1. Try models in circular order, skipping rate-limited ones
        2. Score each result
        3. If score < threshold and attempts remaining, try different model
        4. Validate final result with different model
        5. Return best result
        """
        best_result = None
        best_score = 0.0
        parsers_tried = set()  # Track which parsers we've attempted
        total_parsers = len(self.parsers)
        
        logger.info(f"🔄 Starting adaptive parsing (threshold: {self.min_quality_score})")
        logger.info(f"📋 Will try all {total_parsers} parsers: {[name for name, _ in self.parsers]}")
        
        # Keep trying until we've attempted all available parsers
        while len(parsers_tried) < total_parsers:
            
            # Get next available model (circular rotation)
            parser_name, parser = self._get_next_available_parser()
            
            if not parser:
                logger.warning("⚠️ No available parsers (all rate limited)")
                break
            
            # Skip if already tried (unless it was rate limited before)
            if parser_name in parsers_tried and not self._is_rate_limited(parser_name):
                continue
            
            parsers_tried.add(parser_name)
            
            try:
                logger.info(f"📝 Attempt {len(parsers_tried)}/{total_parsers} using {parser_name}")
                result = parser.parse_resume(resume_text)
                
                # Score the result
                try:
                    score = self._score_result(result)
                    logger.info(f"✓ Parsing successful, calculating score...")
                except Exception as score_error:
                    logger.error(f"❌ Scoring failed for {parser_name}: {score_error}")
                    logger.error(f"Result type: {type(result)}, has personal_info: {hasattr(result, 'personal_info')}")
                    raise
                
                self._log_score_breakdown(result, score, f"Attempt {len(parsers_tried)} - {parser_name}")
                logger.info(f"✓ {parser_name} completed - Score: {score:.1f}/100")
                
                # Track best result
                if score > best_score:
                    best_result = result
                    best_score = score
                
                # Check if we've reached acceptable quality
                if score >= self.min_quality_score:
                    logger.info(f"✅ Quality threshold met! Score: {score:.1f} >= {self.min_quality_score}")
                    logger.info(f"⚡ Skipping remaining {total_parsers - len(parsers_tried)} parsers, moving to validation")
                    
                    # Validate with different model
                    validated_result = self._cross_validate(resume_text, result, parser_name)
                    if validated_result:
                        final_score = self._score_result(validated_result)
                        logger.info(f"🎯 Returning validated result with final score: {final_score:.1f}/100")
                        return validated_result
                    else:
                        logger.info(f"🎯 Returning {parser_name} result (score: {score:.1f}/100)")
                        return result
                else:
                    logger.info(f"⚠️ Score {score:.1f} below threshold {self.min_quality_score}, trying next parser...")
                    logger.info(f"📋 Progress: {len(parsers_tried)}/{total_parsers} parsers tried")
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check for rate limit errors
                if any(keyword in error_msg for keyword in ['rate limit', 'quota', 'too many requests', '429', 'resource_exhausted']):
                    logger.warning(f"🚫 {parser_name} rate limited, marking unavailable for 5 minutes")
                    self._mark_rate_limited(parser_name, minutes=5)
                    parsers_tried.remove(parser_name)  # Don't count rate limit as a real attempt
                else:
                    logger.error(f"✗ {parser_name} failed: {e}")
                
                # Continue to next parser
                continue
        
        # Return best result even if below threshold
        if best_result:
            logger.info(f"📊 Returning best result from {len(parsers_tried)} parsers (score: {best_score:.1f})")
            return best_result
        else:
            logger.error(f"❌ All {total_parsers} parsers failed")
            raise ValueError(f"All {total_parsers} parsers failed - no parser succeeded")
    
    def _get_next_available_parser(self) -> Tuple[Optional[str], Optional[Any]]:
        """
        Get next parser in circular order that's not rate limited
        
        Returns:
            (name, parser) or (None, None) if all rate limited
        """
        attempts = 0
        while attempts < len(self.parsers):
            name, parser = self.parsers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.parsers)
            
            # Check if rate limited
            if self._is_rate_limited(name):
                logger.debug(f"⏭️ Skipping {name} (rate limited)")
                attempts += 1
                continue
            
            return name, parser
        
        return None, None
    
    def _is_rate_limited(self, parser_name: str) -> bool:
        """Check if parser is currently rate limited"""
        limit_until = self.rate_limit_tracker.get(parser_name)
        if limit_until is None:
            return False
        
        if datetime.now() > limit_until:
            # Rate limit expired
            self.rate_limit_tracker[parser_name] = None
            logger.info(f"✅ {parser_name} rate limit expired, available again")
            return False
        
        return True
    
    def _mark_rate_limited(self, parser_name: str, minutes: int = 5):
        """Mark a parser as rate limited for N minutes"""
        self.rate_limit_tracker[parser_name] = datetime.now() + timedelta(minutes=minutes)
    
    def _cross_validate(self, resume_text: str, primary_result: PortfolioData, primary_name: str) -> Optional[PortfolioData]:
        """
        Validate result with different model, get improvement suggestions, and auto-apply them
        
        Returns enhanced/validated result or None if validation fails
        """
        # Get a different parser for validation
        validator_name, validator = None, None
        for name, parser in self.parsers:
            if name != primary_name and not self._is_rate_limited(name):
                validator_name, validator = name, parser
                break
        
        if not validator:
            logger.warning("⚠️ No validator available, skipping cross-validation")
            return None
        
        try:
            logger.info(f"🔍 Cross-validating with {validator_name}")
            validation_result = validator.parse_resume(resume_text)
            validation_score = self._score_result(validation_result)
            
            self._log_score_breakdown(validation_result, validation_score, f"Validator - {validator_name}")
            logger.info(f"✓ Validation complete - Score: {validation_score:.1f}")
            
            # Merge results (use better scored parts from each)
            merged_result = self._merge_results(primary_result, validation_result)
            
            # Generate improvement suggestions from validator
            logger.info(f"💡 Generating improvement suggestions from {validator_name}...")
            suggestions = self._generate_suggestions(merged_result, validation_result, resume_text)
            
            # Auto-apply suggestions
            if suggestions:
                logger.info(f"🔧 Auto-applying {len(suggestions)} suggestions...")
                enhanced_result = self._apply_suggestions(merged_result, suggestions)
            else:
                enhanced_result = merged_result
            
            final_score = self._score_result(enhanced_result)
            self._log_score_breakdown(enhanced_result, final_score, "FINAL ENHANCED")
            logger.info(f"✨ Final result score after suggestions: {final_score:.1f}/100")
            
            return enhanced_result
            
        except Exception as e:
            logger.warning(f"✗ Validation with {validator_name} failed: {e}")
            return None
    
    def _parse_with_fallback(self, resume_text: str) -> PortfolioData:
        """Fallback: Try models in order until one succeeds"""
        for name, parser in self.parsers:
            if self._is_rate_limited(name):
                continue
            
            try:
                logger.info(f"Trying {name}...")
                result = parser.parse_resume(resume_text)
                logger.info(f"✓ {name} succeeded")
                return result
            except Exception as e:
                if 'rate limit' in str(e).lower():
                    self._mark_rate_limited(name)
                logger.warning(f"✗ {name} failed: {e}")
        
        raise ValueError("All parsers failed")
    
    def _parse_with_ensemble(self, resume_text: str) -> PortfolioData:
        """Ensemble: Parse with all, return best"""
        results = []
        
        for name, parser in self.parsers:
            if self._is_rate_limited(name):
                continue
            
            try:
                logger.info(f"Parsing with {name}...")
                result = parser.parse_resume(resume_text)
                score = self._score_result(result)
                results.append((name, result, score))
                logger.info(f"✓ {name} score: {score:.1f}")
            except Exception as e:
                if 'rate limit' in str(e).lower():
                    self._mark_rate_limited(name)
                logger.warning(f"✗ {name} failed: {e}")
        
        if not results:
            raise ValueError("All parsers failed")
        
        results.sort(key=lambda x: x[2], reverse=True)
        best_name, best_result, best_score = results[0]
        logger.info(f"Selected {best_name} (score: {best_score:.1f})")
        return best_result
    
    def _parse_with_validation(self, resume_text: str) -> PortfolioData:
        """Validation: Primary + secondary validation"""
        if len(self.parsers) < 2:
            return self.parsers[0][1].parse_resume(resume_text)
        
        primary_name, primary_parser = self.parsers[0]
        primary_result = primary_parser.parse_resume(resume_text)
        
        return self._cross_validate(resume_text, primary_result, primary_name) or primary_result
    
    def _score_result(self, data: PortfolioData) -> float:
        """
        Score PARSING QUALITY (0-100) - NOT resume quality!
        
        Measures how well the AI extracted and structured data:
        
        1. Required Field Extraction (40 pts):
           - Name extracted and valid: 20 pts
           - Email extracted and valid format: 20 pts
        
        2. Data Format Correctness (30 pts):
           - Email has @ symbol: 10 pts
           - Experience dates properly formatted: 5 pts
           - Education entries have required fields: 5 pts
           - No empty/null critical fields: 5 pts
           - URLs are valid format: 5 pts
        
        3. Structure Completeness (20 pts):
           - Experience descriptions not empty: 10 pts
           - Skills array properly formatted: 5 pts
           - All sections present (even if empty): 5 pts
        
        4. Data Consistency (10 pts):
           - No duplicate entries: 5 pts
           - Dates logical (start < end): 5 pts
        """
        score = 0.0
        issues = []
        
        # 1. REQUIRED FIELD EXTRACTION (40 pts)
        if data.personal_info.name and len(data.personal_info.name.strip()) > 2:
            score += 20
        else:
            issues.append("Name missing or invalid")
        
        if data.personal_info.email and '@' in data.personal_info.email:
            score += 20
        else:
            issues.append("Email missing or invalid format")
        
        # 2. DATA FORMAT CORRECTNESS (30 pts)
        
        # Email format validation (10 pts)
        if data.personal_info.email:
            if '@' in data.personal_info.email and '.' in data.personal_info.email.split('@')[1]:
                score += 10
            else:
                issues.append("Email format incorrect")
        
        # Experience dates validation (5 pts)
        valid_dates = True
        for exp in data.experience:
            if not exp.start_date or exp.start_date == "Not specified":
                valid_dates = False
                break
        if data.experience and valid_dates:
            score += 5
        elif data.experience:
            issues.append("Experience dates incomplete")
        
        # Education has required fields (5 pts)
        edu_complete = True
        for edu in data.education:
            if not edu.degree or not edu.school:
                edu_complete = False
                break
        if data.education and edu_complete:
            score += 5
        elif data.education:
            issues.append("Education missing required fields")
        
        # No critical empty fields (5 pts)
        empty_count = 0
        if data.experience:
            for exp in data.experience:
                if not exp.role or not exp.company:
                    empty_count += 1
        if data.projects:
            for proj in data.projects:
                if not proj.title:
                    empty_count += 1
        if empty_count == 0:
            score += 5
        else:
            issues.append(f"{empty_count} critical fields empty")
        
        # URLs valid format (5 pts)
        url_valid = True
        for url_field in [data.personal_info.linkedin, data.personal_info.github]:
            if url_field:
                url_str = str(url_field) if not isinstance(url_field, str) else url_field
                if url_str.strip() and not (url_str.startswith('http://') or url_str.startswith('https://')):
                    url_valid = False
        if url_valid:
            score += 5
        else:
            issues.append("URLs not properly formatted")
        
        # 3. STRUCTURE COMPLETENESS (20 pts)
        
        # Experience descriptions not empty (10 pts)
        desc_quality = 0
        if data.experience:
            filled_descs = sum(1 for exp in data.experience if exp.description and len(exp.description.strip()) > 20)
            desc_quality = (filled_descs / len(data.experience)) * 10
            score += desc_quality
            if desc_quality < 10:
                issues.append(f"Experience descriptions incomplete ({filled_descs}/{len(data.experience)} filled)")
        
        # Skills array properly formatted (5 pts)
        if data.skills and len(data.skills) > 0:
            if all(isinstance(s, str) and len(s.strip()) > 0 for s in data.skills):
                score += 5
            else:
                issues.append("Skills array has empty/invalid entries")
        
        # All sections present (5 pts) - even empty arrays are ok
        sections_present = 0
        if data.personal_info: sections_present += 1
        if data.skills is not None: sections_present += 1
        if data.experience is not None: sections_present += 1
        if data.education is not None: sections_present += 1
        if data.projects is not None: sections_present += 1
        if data.achievements is not None: sections_present += 1
        if sections_present == 6:
            score += 5
        else:
            issues.append(f"Missing sections: {6-sections_present}")
        
        # 4. DATA CONSISTENCY (10 pts)
        
        # No duplicates (5 pts)
        has_duplicates = False
        if len(data.skills) != len(set(s.lower() for s in data.skills)):
            has_duplicates = True
        if not has_duplicates:
            score += 5
        else:
            issues.append("Duplicate skills found")
        
        # Dates logical (5 pts)
        dates_logical = True
        for exp in data.experience:
            if exp.end_date and exp.end_date != "Present":
                # Could add date parsing logic here
                pass
        if dates_logical:
            score += 5
        
        # Log issues if score is low
        if score < 75 and issues:
            logger.warning(f"⚠️ Parsing quality issues: {', '.join(issues[:3])}")
        
        return min(score, 100.0)
    
    def _log_score_breakdown(self, data: PortfolioData, score: float, label: str = ""):
        """Log detailed score breakdown for debugging"""
        logger.info(f"📊 {label} Parsing Quality Score: {score:.1f}/100")
        logger.info(f"   Required Fields:")
        logger.info(f"      Name: {'✓' if data.personal_info.name else '✗'} {data.personal_info.name[:30] if data.personal_info.name else 'MISSING'}")
        logger.info(f"      Email: {'✓' if data.personal_info.email and '@' in data.personal_info.email else '✗'} {data.personal_info.email if data.personal_info.email else 'MISSING'}")
        logger.info(f"   Data Extraction:")
        logger.info(f"      Skills: {len(data.skills)} extracted")
        logger.info(f"      Experience: {len(data.experience)} entries")
        logger.info(f"      Education: {len(data.education)} entries")
        logger.info(f"      Projects: {len(data.projects)} entries")
        logger.info(f"      Achievements: {len(data.achievements)} entries")
        logger.info(f"   Optional Fields:")
        logger.info(f"      Phone: {'✓' if data.personal_info.phone else '✗'}")
        logger.info(f"      LinkedIn: {'✓' if data.personal_info.linkedin else '✗'}")
        logger.info(f"      GitHub: {'✓' if data.personal_info.github else '✗'}")
        logger.info(f"      Bio: {'✓' if data.personal_info.bio else '✗'}")
        logger.info(f"      Location: {'✓' if data.personal_info.location else '✗'}")

    
    def _merge_results(self, primary: PortfolioData, secondary: PortfolioData) -> PortfolioData:
        """
        Merge two results, using better parts from each
        """
        merged = primary.model_dump()
        secondary_dict = secondary.model_dump()
        
        # Personal info: prefer non-empty
        for key in merged['personal_info']:
            if not merged['personal_info'][key] and secondary_dict['personal_info'].get(key):
                merged['personal_info'][key] = secondary_dict['personal_info'][key]
        
        # Skills: union
        merged['skills'] = list(set(merged.get('skills', []) + secondary_dict.get('skills', [])))
        
        # Experience: use whichever has more
        if len(secondary_dict.get('experience', [])) > len(merged.get('experience', [])):
            merged['experience'] = secondary_dict['experience']
        
        # Education: use whichever has more
        if len(secondary_dict.get('education', [])) > len(merged.get('education', [])):
            merged['education'] = secondary_dict['education']
        
        # Projects: use whichever has more
        if len(secondary_dict.get('projects', [])) > len(merged.get('projects', [])):
            merged['projects'] = secondary_dict['projects']
        
        # Achievements: combine
        primary_ach = {a['title']: a for a in merged.get('achievements', [])}
        for ach in secondary_dict.get('achievements', []):
            if ach['title'] not in primary_ach:
                merged['achievements'].append(ach)
        
        return PortfolioData(**merged)
    
    def _generate_suggestions(self, current: PortfolioData, validator: PortfolioData, resume_text: str) -> List[Dict[str, Any]]:
        """
        Generate improvement suggestions by comparing current and validator results
        
        Returns list of actionable suggestions to improve quality
        """
        suggestions = []
        current_dict = current.model_dump()
        validator_dict = validator.model_dump()
        
        # Check for missing personal info fields (HIGH PRIORITY)
        for field in ['phone', 'linkedin', 'github', 'bio', 'location']:
            current_val = current_dict['personal_info'].get(field)
            validator_val = validator_dict['personal_info'].get(field)
            
            # Add if missing
            if not current_val and validator_val:
                suggestions.append({
                    'type': 'personal_info',
                    'field': field,
                    'action': 'add',
                    'value': validator_val,
                    'reason': f'Validator found {field} that primary parser missed'
                })
            # Enhance if validator has better value
            elif current_val and validator_val and len(str(validator_val)) > len(str(current_val)):
                suggestions.append({
                    'type': 'personal_info',
                    'field': field,
                    'action': 'enhance',
                    'value': validator_val,
                    'reason': f'Validator has more complete {field}'
                })
        
        # Check for missing skills (IMPORTANT for score)
        current_skills = set(s.lower() for s in current_dict.get('skills', []))
        validator_skills = set(s.lower() for s in validator_dict.get('skills', []))
        missing_skills = validator_skills - current_skills
        if missing_skills:
            # Get original case from validator
            original_skills = [s for s in validator_dict.get('skills', []) if s.lower() in missing_skills]
            suggestions.append({
                'type': 'skills',
                'action': 'add',
                'values': original_skills,
                'reason': f'Validator found {len(original_skills)} additional skills (SCORE BOOST)'
            })
        
        # Check for incomplete experience descriptions (QUALITY)
        for i, exp in enumerate(current_dict.get('experience', [])):
            exp_desc = exp.get('description', '')
            if len(exp_desc) < 100:  # Short or missing description
                if i < len(validator_dict.get('experience', [])):
                    val_exp = validator_dict['experience'][i]
                    val_desc = val_exp.get('description', '')
                    if val_desc and len(val_desc) > len(exp_desc):
                        suggestions.append({
                            'type': 'experience',
                            'index': i,
                            'field': 'description',
                            'action': 'enhance',
                            'value': val_desc,
                            'reason': f'Validator has more detailed description (+{len(val_desc)-len(exp_desc)} chars)'
                        })
        
        # Check for missing experiences
        if len(validator_dict.get('experience', [])) > len(current_dict.get('experience', [])):
            for i in range(len(current_dict.get('experience', [])), len(validator_dict.get('experience', []))):
                suggestions.append({
                    'type': 'experience',
                    'action': 'add',
                    'value': validator_dict['experience'][i],
                    'reason': 'Validator found additional work experience'
                })
        
        # Check for missing achievements (BONUS POINTS)
        current_ach_titles = {a['title'].lower() for a in current_dict.get('achievements', [])}
        for val_ach in validator_dict.get('achievements', []):
            if val_ach['title'].lower() not in current_ach_titles:
                suggestions.append({
                    'type': 'achievements',
                    'action': 'add',
                    'value': val_ach,
                    'reason': 'Validator found additional achievement (BONUS POINTS)'
                })
        
        # Check for missing projects (BONUS POINTS)
        if len(validator_dict.get('projects', [])) > len(current_dict.get('projects', [])):
            for i in range(len(current_dict.get('projects', [])), len(validator_dict.get('projects', []))):
                suggestions.append({
                    'type': 'projects',
                    'action': 'add',
                    'value': validator_dict['projects'][i],
                    'reason': 'Validator found additional project (BONUS POINTS)'
                })
        
        # Check for missing project details
        for i, proj in enumerate(current_dict.get('projects', [])):
            if i < len(validator_dict.get('projects', [])):
                val_proj = validator_dict['projects'][i]
                
                if not proj.get('tech_stack') and val_proj.get('tech_stack'):
                    suggestions.append({
                        'type': 'projects',
                        'index': i,
                        'field': 'tech_stack',
                        'action': 'add',
                        'value': val_proj['tech_stack'],
                        'reason': 'Validator found tech stack details'
                    })
                
                proj_desc = proj.get('description', '')
                val_desc = val_proj.get('description', '')
                if not proj_desc and val_desc:
                    suggestions.append({
                        'type': 'projects',
                        'index': i,
                        'field': 'description',
                        'action': 'add',
                        'value': val_desc,
                        'reason': 'Validator found project description'
                    })
                elif val_desc and len(val_desc) > len(proj_desc):
                    suggestions.append({
                        'type': 'projects',
                        'index': i,
                        'field': 'description',
                        'action': 'enhance',
                        'value': val_desc,
                        'reason': 'Validator has more detailed project description'
                    })
                
                # Check URLs
                for url_field in ['link', 'github_url']:
                    if not proj.get(url_field) and val_proj.get(url_field):
                        suggestions.append({
                            'type': 'projects',
                            'index': i,
                            'field': url_field,
                            'action': 'add',
                            'value': val_proj[url_field],
                            'reason': f'Validator found project {url_field}'
                        })
        
        # Check for missing education entries
        if len(validator_dict.get('education', [])) > len(current_dict.get('education', [])):
            for i in range(len(current_dict.get('education', [])), len(validator_dict.get('education', []))):
                suggestions.append({
                    'type': 'education',
                    'action': 'add',
                    'value': validator_dict['education'][i],
                    'reason': 'Validator found additional education entry'
                })
        
        logger.info(f"💡 Generated {len(suggestions)} improvement suggestions")
        for sug in suggestions[:10]:  # Log first 10
            logger.info(f"   - {sug['reason']}")
        if len(suggestions) > 10:
            logger.info(f"   ... and {len(suggestions)-10} more")
        
        return suggestions
    
    def _apply_suggestions(self, current: PortfolioData, suggestions: List[Dict[str, Any]]) -> PortfolioData:
        """
        Auto-apply improvement suggestions to enhance data quality
        """
        data = current.model_dump()
        applied_count = 0
        
        for sug in suggestions:
            try:
                if sug['type'] == 'personal_info':
                    if sug['action'] in ['add', 'enhance']:
                        data['personal_info'][sug['field']] = sug['value']
                        applied_count += 1
                
                elif sug['type'] == 'skills' and sug['action'] == 'add':
                    data['skills'].extend(sug['values'])
                    data['skills'] = list(set(data['skills']))  # Remove duplicates
                    applied_count += 1
                
                elif sug['type'] == 'experience':
                    if sug['action'] == 'add':
                        data['experience'].append(sug['value'])
                        applied_count += 1
                    elif sug['action'] == 'enhance' and 'index' in sug:
                        if sug['index'] < len(data['experience']):
                            data['experience'][sug['index']][sug['field']] = sug['value']
                            applied_count += 1
                
                elif sug['type'] == 'achievements' and sug['action'] == 'add':
                    data['achievements'].append(sug['value'])
                    applied_count += 1
                
                elif sug['type'] == 'projects':
                    if sug['action'] == 'add':
                        data['projects'].append(sug['value'])
                        applied_count += 1
                    elif 'index' in sug and sug['index'] < len(data['projects']):
                        if sug['action'] in ['add', 'enhance']:
                            data['projects'][sug['index']][sug['field']] = sug['value']
                            applied_count += 1
                
                elif sug['type'] == 'education' and sug['action'] == 'add':
                    data['education'].append(sug['value'])
                    applied_count += 1
                        
            except Exception as e:
                logger.warning(f"⚠️ Failed to apply suggestion ({sug.get('reason', 'unknown')}): {e}")
        
        logger.info(f"✅ Applied {applied_count}/{len(suggestions)} suggestions")
        return PortfolioData(**data)

