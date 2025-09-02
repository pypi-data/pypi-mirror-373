""" 
    MIT License

    Copyright (c) 2025 1bali1

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""
import json
import os
import logging
from enum import Enum
from quart import request, g, render_template as quart_render_template, Quart
from .errors import (
    ConfigNotFoundError,
    InvalidConfigError,
    MissingPageError,
    LanguageNotSupportedError,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"
    

class I18n:
    """
    Localization manager for Quart applications.

    Handles loading JSON-based localization files for multiple languages,
    injecting localized strings into templates, and rendering templates
    with optional dynamic context safely.

    Attributes:
        app (Quart): The Quart application instance.
        languages (list[str]): List of supported language codes (e.g., ["en", "hu"]).
        defaultLanguage (str): Default language code used when no translation is found.
        configPath (str): Directory path containing JSON localization files.
        configList (list[str]): List of JSON files in the configPath.
        langMap (dict): Cached localization data: lang -> page.json -> dict.
    """
    def __init__(self, appInstance: Quart, languages: list, configPath: str = None, defaultLanguage = "en"):
        """
        Initialize the I18n manager.

        Args:
            appInstance (Quart): Quart application instance.
            languages (list[str]): List of supported language codes.
            configPath (str): Path to the JSON localization files directory.
            defaultLanguage (str, optional): Default language code. Defaults to "en".

        Raises:
            ValueError: If languages list is empty.
            ConfigNotFoundError: If configPath does not exist.
        """
        self.app = appInstance
        self.defaultLanguage = defaultLanguage
        self.languages = languages
        
        if not languages:
            raise ValueError("Enter a valid languages list!")
        if not os.path.isdir(configPath): raise ConfigNotFoundError("No dir found with the given config path!")
        
        self.configPath = configPath
        self.configList = os.listdir(configPath)
        self.langMap = {}
        
        for lang in self.languages:
            self.langMap[lang] = {}
            
        self.loadConfig()
        self.app.context_processor(self.injectLocalizationToTemplate)

    
    def injectLocalizationToTemplate(self):
        """
        Injects current language and localization dictionary into Jinja templates.

        Returns:
            dict: Dictionary with:
                - 'lang': current language code
                - 't': localized strings dictionary for the current page
        """
        return {
            "lang": getattr(g, "currentLanguage", self.defaultLanguage),
            "t": getattr(g, "localizations", {})
        }
    
    async def render_template(self, template_name, **context):
        """
        Async wrapper for Quart's render_template, injecting localization.

        Args:
            template_name (str): Template file name (e.g., "index.html").
            context (dict, optional): Context variables for template rendering.

        Returns:
            Response: Rendered Quart template response.

        Raises:
            MissingPageError: If JSON config for the page does not exist.
        """
        pageName = template_name.replace(".html", "") # Hate to use snake_case 
        if f"{pageName}.json" not in self.configList: raise MissingPageError("No config file found with the given page name!")
        languageCookie = request.cookies.get("language", self.defaultLanguage)

        primaryLangCode = languageCookie.split(",")[0].split("-")[0].lower() 
        currentLanguage = primaryLangCode
        if primaryLangCode not in self.languages:
            currentLanguage = self.defaultLanguage

        
        g.currentLanguage = currentLanguage
        g.localizations = self.getLocalization(currentLanguage, pageName)

        if context:
            g.localizations = {
                k: (v.format_map(SafeDict(context)) if isinstance(v, str) else v)
                for k, v in g.localizations.items()
            }


        return await quart_render_template(template_name, **context)
    
    def loadConfig(self):
        """
        Load all JSON localization files into memory.

        Raises:
            InvalidConfigError: If JSON parsing fails.
            ConfigNotFoundError: If configPath does not exist.
        """
        if not os.path.isdir(self.configPath): raise ConfigNotFoundError("No dir found with the given config path!")
        for config in os.listdir(self.configPath):
            with open(f"{self.configPath}/{config}", "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    for lang in self.languages:
                        self.langMap[lang][config] = data[lang]
                except:
                    raise InvalidConfigError("There was an error while the app was trying to encode the localization config!")
   
    def getLocalization(self, lang: str, page: str):
        """
        Retrieve the localization dictionary for a given language and page.

        Args:
            lang (str): Language code.
            page (str): Page name corresponding to a JSON file (without ".json").

        Returns:
            dict: Dictionary of localized strings.

        Raises:
            ConfigNotFoundError: If configPath, page, or language data is missing.
        """
        if not os.path.isdir(self.configPath): raise ConfigNotFoundError("No dir found with the given config path!")
        if f"{page}.json" not in os.listdir(self.configPath):
            raise ConfigNotFoundError("No localization config found with the given page name!")

        data = self.langMap.get(lang, None)
        if data is None:
            raise ConfigNotFoundError("No localization config found with the given language!")
        
        data = data[f"{page}.json"]
        
        if data is None:
            logger.warning(f"No localization found for page '{page}' for the language '{lang}'")
            return {}

        return data
    