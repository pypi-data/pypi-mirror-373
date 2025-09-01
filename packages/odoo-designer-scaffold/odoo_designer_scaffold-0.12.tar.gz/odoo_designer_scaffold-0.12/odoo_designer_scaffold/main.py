import sys
import re

from io import BytesIO
from zipfile import ZipFile
from PIL import Image
from base64 import b64decode

def create_zip(zip_file, name, version, with_python, website_number, theme_number):
    
    if with_python:
        compute_name = 'website_%s_backend' % (name)
        python_manifest = create_python_module_manifest(zip_file, compute_name, version)
        zip_file.writestr(compute_name+'/__manifest__.py', python_manifest)
        zip_file.writestr(compute_name+'/__init__.py', '# -*- coding: utf-8 -*-')
        zip_file.writestr(compute_name+'/models/__init__.py', '# -*- coding: utf-8 -*-')
        zip_file.writestr(compute_name+'/tests/','')

    if website_number == 1 :
        compute_name = 'website_%s' % (name)
        create_website_module(zip_file, compute_name, version)
    else:
        while website_number > 0:
            compute_name = 'website_%s_%s' % (name,website_number)
            create_website_module(zip_file, compute_name, version)
            website_number -= 1

    if theme_number == 1 :
        compute_name = 'theme_%s' % (name)
        create_theme_module(zip_file, compute_name, version)
    else:
        while theme_number > 0:
            compute_name = 'theme_%s_%s' % (name,theme_number)
            create_theme_module(zip_file, compute_name, version)
            theme_number -= 1


def create_website_module(zip_file, name, version):
    manifest_file = create_module_manifest(name, version)
    zip_file.writestr(name+'/__manifest__.py',manifest_file)
    zip_file.writestr(name+'/__init__.py', '# -*- coding: utf-8 -*-')
    zip_file.writestr(name+'/controllers/__init__.py', '# -*- coding: utf-8 -*-')
    create_module_static_files(zip_file, name)
    create_scss_static_files(zip_file, name)

def create_theme_module(zip_file, name, version):
    manifest_file = create_theme_manifest(name, version)
    zip_file.writestr(name+'/__manifest__.py',manifest_file)
    create_theme_static_files(zip_file, name)
    create_scss_static_files(zip_file, name)

def create_module_manifest(name, version):
    return """{
        'name': '"""+name+"""',
        'version': '"""+version+""".0.0',
        'depends': ['website'],
        'license': 'LGPL-3',
        'data': [
            # Images
            'data/images.xml',
            # Menu
            'data/menu.xml',
            # Presets
            'data/presets.xml',
            # Static pages
            'data/pages/home.xml',
            # Views 
            'views/website_templates.xml'
        ],
        'assets': {
            'web.assets_frontend': [
                # Global QWeb JS Templates
                '"""+name+"""/static/src/xml/example.xml',
               
            ],
        },
        'cloc_exclude': [
            'lib/**/*',
            'data/**/*'
        ],
    }"""

def create_theme_manifest(name, version):
    return """{
        'name': '"""+name+"""',
        'version': '"""+version+""".0.0',
        'depends': ['website'],
        'license': 'LGPL-3',
        'data': [
            # Views
            'views/snippets/options.xml',
            'views/snippets/s_wd_snippet.xml',
        ],
        'assets': {
            'web._assets_primary_variables': [
                '"""+name+"""/static/src/scss/primary_variables.scss',
            ],
            'web._assets_frontend_helpers': [
                ('prepend', '"""+name+"""/static/src/scss/bootstrap_overridden.scss'),
            ],
            'web.assets_frontend': [
                # LIB
                # Lib name
                # '"""+name+"""/static/src/lib/libname/libname.min.css',
                # '"""+name+"""/static/src/lib/libname/libname.min.js', 
                # SCSS
                # Base
                '"""+name+"""/static/src/scss/base/variables.scss',
                '"""+name+"""/static/src/scss/base/functions.scss',
                '"""+name+"""/static/src/scss/base/mixins.scss',
                #'"""+name+"""/static/src/scss/base/fonts.scss',
                '"""+name+"""/static/src/scss/base/icons.scss',
                '"""+name+"""/static/src/scss/base/helpers.scss',
                '"""+name+"""/static/src/scss/base/typography.scss',
                # Components
                #'"""+name+"""/static/src/scss/components/*.scss',
                # Layout
                '"""+name+"""/static/src/scss/layout/body.scss',
                '"""+name+"""/static/src/scss/layout/header.scss',
                '"""+name+"""/static/src/scss/layout/footer.scss',
                '"""+name+"""/static/src/scss/layout/blog.scss',
                # Pages
                '"""+name+"""/static/src/scss/pages/home.scss',
                # Standard Snippets Overrides
                '"""+name+"""/static/src/scss/snippets/cookies_bar.scss',
                # Custom Snippets
                #'"""+name+"""/static/src/snippets/s_wd_snippet/000.scss',
                #'"""+name+"""/static/src/snippets/s_wd_snippet/000.xml',
                #'"""+name+"""/static/src/snippets/s_wd_snippet/000.js',
            ],
            'website.assets_wysiwyg': [
                '"""+name+"""/static/src/snippets/s_wd_snippet/options.js'
            ]
        },
        'cloc_exclude': [
            'static/src/scss/bootstrap_overridden.scss',
            'static/src/scss/primary_variables.scss',
            'lib/**/*',
            'data/**/*'
        ],
    }"""

def create_python_module_manifest(zip_file, name, version):
    return """{
        'name': '"""+name+"""',
        'version': '"""+version+"""0.0',
        'depends': [],
        'license': 'LGPL-3',
        'data': [],
        'assets': {},
    }"""

def create_theme_static_files(zip_file, name):
    cookies_bar = """// ------------------------------------------------------------------------------ //
    // STANDARD SNIPPET - Minor style changes of existing snippet
    // ------------------------------------------------------------------------------ //"""

    snippet_scss = """.s_wd_snippet {
        
    }"""

    snippet_xml = """<?xml version="1.0" encoding="utf-8"?>
    <templates>
        <t t-name=\""""+name+""".s_wd_snippet">
            <!-- Your markup here -->
        </t>
    </templates>"""

    option = """<?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <!-- Add custom snippets -->
        <template id="snippets" inherit_id="website.snippets" name="Scaffold - Snippets">
            <xpath expr="//*[@id='default_snippets']" position="before">
                <t id="x_wd_snippets">
                    <div id="x_snippets_category_static" class="o_panel">
                        <div class="o_panel_header">Scaffold</div>
                        <div class="o_panel_body">
                            <t t-snippet=\""""+name+""".s_wd_snippet" t-thumbnail="/"""+name+"""/static/src/img/wbuilder/snippet_thumbnail.svg">
                                <keywords>Custom, Snippet</keywords>
                            </t>
                        </div>
                    </div>
                </t>
            </xpath>
        </template>

        <!-- Website builder: Global options -->
        <template id="snippet_options" inherit_id="website.snippet_options" name="Scaffold - Snippets Options">
            <!-- Insert your options here within an Xpath -->
        </template>
    </odoo>"""

    s_wd_snippet = """<?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <template id="s_wd_snippet" name="Custom Snippet">
            <section class="s_wd_snippet o_cc o_cc1 pt48 pb48">
                <div class="container s_allow_columns">
                    <!-- Your content here -->
                    <h1 class="text-center display-1">Welcome</h1>
                    <p class="text-center">Hello my dear Odooer!</p>
                    <br />
                    <img src="/web/image/"""+name+""".img_s_wd_snippet_default" class="img img-fluid mx-auto d-block text-center" alt="Default Image" />
                </div>
            </section>
        </template>
    </odoo>"""

    # Snippets
    zip_file.writestr(name+'/static/src/scss/snippets/cookies_bar.scss',cookies_bar)
    zip_file.writestr(name+'/static/src/scss/snippets/s_wd_snippet/000.js','')
    zip_file.writestr(name+'/static/src/scss/snippets/s_wd_snippet/000.scss',snippet_scss)
    zip_file.writestr(name+'/static/src/scss/snippets/s_wd_snippet/000.xml',snippet_xml)
    zip_file.writestr(name+'/static/src/scss/snippets/s_wd_snippet/options.js','')

    # Views
    zip_file.writestr(name+'/views/snippets/options.xml',option)
    zip_file.writestr(name+'/views/snippets/s_wd_snippet.xml',s_wd_snippet)

def create_scss_static_files(zip_file, name):
    bootstrap = """// Override any bootstrap variable from here.

    $grid-gutter-width: 30px;
    $enable-rfs: true;"""

    bootsrap_latest ="""/// As the number of lines of code can be critic: 
    // Feel free to just extend the utility classes manually (without Bootstrap Utilities API and boostrap_utilities.scss).
    // Newly created variables have to be located in the base/variables.scss as this is the first SCSS file called.

    // Classes
    // .fw-medium { font-weight: $font-weight-medium; }
    // .fw-semibold { font-weight: $font-weight-semibold; }"""

    functions = """// ------------------------------------------------------------------------------ //
    // FUNCTIONS - (Only return/compute values, no CSS selectors output)
    // ------------------------------------------------------------------------------ //

    /**
    * Explanation of your function
    *
    * @param {Type} $variable - Explanation about this variable
    * 
    * Usage:
    * @include my-function($variable);
    */
    /*
    @function my-function($variable: default) {
        @return $result;
    }
    */"""

    helpers = """// ------------------------------------------------------------------------------ //
    // HELPERS - (Global classes used across the whole website)
    // ------------------------------------------------------------------------------ //"""

    icons = """// ------------------------------------------------------------------------------ //
    // ICONS - Custom Icon Font Set
    // ------------------------------------------------------------------------------ //

    /*
    @font-face {
        font-family: 'scaffold-icons';
        src: url('../../fonts/scaffold-icons.woff?wyfr5p') format('woff');
        font-weight: normal;
        font-style: normal;
        font-display: block;
    }

    .x_wd_icon {
        // Use !important to prevent issues with browser extensions that change fonts
        font-family: 'materrup-icons' !important;
        speak: never;
        font-style: normal;
        font-weight: normal;
        font-variant: normal;
        text-transform: none;
        line-height: 1;

        // Better Font Rendering
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    .x_wd_icon_arrow_left:before { content: '\f001'; }
    */"""

    mixins = """// ------------------------------------------------------------------------------ //
    // MIXINS
    // ------------------------------------------------------------------------------ //

    /**
    * Explanation of your mixin
    *
    * @param {Type} $variable - Explanation about this variable
    * 
    * Usage:
    * @include my-mixin($variable);
    */
    /*
    @mixin my-mixin($variable: default) {


    }
    */"""

    placeholders = """// ------------------------------------------------------------------------------ //
    // PLACEHOLDERS - All %placeholder declarations
    // ------------------------------------------------------------------------------ //"""

    typography = """// ------------------------------------------------------------------------------ //
    // TYPOGRAPHY - Everything related to font style helpers (headings, font-weights, etc)
    // ------------------------------------------------------------------------------ //

    strong, b {}
    em, i {}"""

    variables = """// ------------------------------------------------------------------------------ //
    // VARIABLES - Custom SASS and CSS Variables
    // ------------------------------------------------------------------------------ //

    // Set your global SASS variable here:
    // $custom-sass-variable: value;

    :root {
        // Set your CSS variables here: 
        // --my-variable: value;
    }"""

    blog = """// ------------------------------------------------------------------------------ //
    // WEBSITE BLOG - Styles used on multiple views within the blog App.
    // ------------------------------------------------------------------------------ //
    #wrap.website_blog {

    }"""

    body = """// ------------------------------------------------------------------------------ //
    // BODY
    // ------------------------------------------------------------------------------ //
    body {
        // For exemaple: 
        // -webkit-font-smoothing: antialiased;
        // -moz-osx-font-smoothing: grayscale;
    }"""

    footer = """// ------------------------------------------------------------------------------ //
    // FOOTER
    // ------------------------------------------------------------------------------ //
    .x_wd_footer {

    }"""

    header = """// ------------------------------------------------------------------------------ //
    // HEADER
    // ------------------------------------------------------------------------------ //
    .x_wd_header {

    }"""

    home_scss = """// ------------------------------------------------------------------------------ //
    // HOME PAGE
    // ------------------------------------------------------------------------------ //
    .x_wd_page_home {

    }"""

    primary_var="""// ------------------------------------------------------------------------------ //
    // PRESETS
    // ------------------------------------------------------------------------------ //
    $o-website-values-palettes: (
        (
            // Colors
            'color-palettes-name':              '"""+name+"""',

            // Fonts
            'font':                             'Inter',
            'headings-font':                    'Caveat',
            'navbar-font':                      'Inter',
            'buttons-font':                     'Inter',

            // Header
            'header-template':                  '"""+name+"""',
            'header-font-size':                 1rem,
            'logo-height':                      1.5rem,
            'fixed-logo-height':                1rem,

            // Footer
            'footer-template':                  '"""+name+"""'
        ),
    );

    // ------------------------------------------------------------------------------ //
    // FONTS
    // ------------------------------------------------------------------------------ //
    $o-theme-font-configs: (
        'Caveat': (
            'family':   ('Caveat', cursive),
            'url':      'Caveat:400,500,700',
            'properties' : (
                'base': (
                    'font-size-base': 1rem
                )
            )
        ),
        'Inter': (
            'family':   ('Inter', sans-serif),
            'url':      'Inter:400,400i,500,500i,700,700i',
            'properties': (
                'base': (
                    'font-size-base': 1rem
                )
            )
        ),
    );

    // ------------------------------------------------------------------------------ //
    // COLORS
    // ------------------------------------------------------------------------------ //
    $o-color-palettes: map-merge($o-color-palettes,
        (
            '"""+name+"""': (
                'o-color-1': #714B67, // Primary
                'o-color-2': #017E84, // Secondary
                'o-color-3': #F3F4F6, // Light
                'o-color-4': #FFFFFF, // Whitish
                'o-color-5': #111827, // Blackish

                'menu':        2,
                'footer':      5
            )
        )
    );

    $o-user-gray-color-palette: (
        'white': #FFFFFF,
        '100':   #E6E7E8,
        '200':   #D1D2D4,
        '300':   #BCBDBF,
        '400':   #A8A9AC,
        '500':   #949598,
        '600':   #818285,
        '700':   #6D6E71,
        '800':   #58585A,
        '900':   #3A3A3B,
        'black': #292929
    );

    $o-user-theme-color-palette: (
        'success': #00C35A,
        'danger':  #D72F3D,
        'warning': #FFB82A, 
        'info':    #2F72D7,
        'light':   #FFF2E9,
        'dark':    #505050
    );"""

    theme="""#wrapwrap {  
        > header {}
        > main {}
        > footer {}
    }"""

    # Style    
    zip_file.writestr(name+'/static/src/scss/bootstrap_overridden.scss',bootstrap)
    zip_file.writestr(name+'/static/src/scss/bootstrap_latest.scss',bootsrap_latest)
    zip_file.writestr(name+'/static/src/scss/primary_variables.scss',primary_var)
    zip_file.writestr(name+'/static/src/scss/theme.scss',theme)
        # Base
    zip_file.writestr(name+'/static/src/scss/base/functions.scss',functions)
    zip_file.writestr(name+'/static/src/scss/base/helpers.scss',helpers)
    zip_file.writestr(name+'/static/src/scss/base/icons.scss',icons)
    zip_file.writestr(name+'/static/src/scss/base/mixins.scss',mixins)
    zip_file.writestr(name+'/static/src/scss/base/placeholders.scss',placeholders)
    zip_file.writestr(name+'/static/src/scss/base/typography.scss',typography)
    zip_file.writestr(name+'/static/src/scss/base/variables.scss',variables)
        # Layout
    zip_file.writestr(name+'/static/src/scss/layout/blog.scss',blog)
    zip_file.writestr(name+'/static/src/scss/layout/body.scss',body)
    zip_file.writestr(name+'/static/src/scss/layout/footer.scss',footer)
    zip_file.writestr(name+'/static/src/scss/layout/header.scss',header)
        # Pages
    zip_file.writestr(name+'/static/src/scss/pages/home.scss',home_scss)

def create_module_static_files(zip_file, name):
    home = """<?xml version="1.0" encoding="utf-8"?>
    <odoo noupdate="1">
        <record id="page_home" model="website.page">
            <field name="name">Home</field>
            <field name="is_published" eval="True" />
            <field name="key">"""+name+""".page_home</field>
            <field name="url">/</field>
            <field name="type">qweb</field>
            <field name="website_id" eval="1" />
            <field name="arch" type="xml">
                <t name="Accueil" t-name=\""""+name+""".page_home">
                    <t t-call="website.layout">
                        <!-- <title> in the <head> -->
                        <t t-set="additional_title" t-valuef="Home" />
                        <!-- body classes -->
                        <t t-set="pageName" t-valuef="x_wd_page_home" />

                        <div id="wrap" class="oe_structure">
                            <!-- Your building blocks here -->
                            <section class="s_wd_snippet o_cc o_cc1 pt48 pb48" data-snippet="s_wd_snippet" data-name="Custom Snippet">
                                <div class="container s_allow_columns">
                                    <h1 class="text-center display-1">Welcome</h1>
                                    <p class="text-center">Hello my dear Odooer!</p>
                                    <br />
                                    <img src="/web/image/"""+name+""".img_s_wd_snippet_default" class="img img-fluid mx-auto d-block text-center" alt="Default Image" />
                                </div>
                            </section>
                        </div>
                    </t>
                </t>
            </field>
        </record>
    </odoo>"""

    menu = """<?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <!-- Default Homepage
        <delete model="website.menu" search="[('url','in', ['/', '/']), ('website_id', '=', 1)]"/>

        <record id="menu_example" model="website.menu">
            <field name="name">Example</field>
            <field name="url">/example</field>
            <field name="parent_id" search="[
                ('url', '=', '/default-main-menu'),
                ('website_id', '=', 1)]"/>
            <field name="website_id">1</field>
            <field name="sequence" type="int">20</field>
        </record> 
        -->
    </odoo>"""

    images= """<?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <!-- Branding -->
        <record id="logo" model="ir.attachment">
            <field name="name">Logo</field>
            <field name="datas" type="base64" file=\""""+name+"""/static/src/img/content/logo.svg"/>
            <field name="res_model">ir.ui.view</field>
            <field name="public" eval="True"/>
        </record>

        <record id="website.default_website" model="website">
            <field name="logo" type="base64" file=\""""+name+"""/static/src/img/content/logo.svg"/>
        </record>

        <!-- Snippets -->
        <record id="img_s_wd_snippet_default" model="ir.attachment">
            <field name="name">Default Custom Snippet Image</field>
            <field name="datas" type="base64" file=\""""+name+"""/static/src/img/content/snippets/s_wd_snippet/logo.png"/>
            <field name="res_model">ir.ui.view</field>
            <field name="public" eval="True"/>
        </record>
    </odoo>
    """

    presets = """<?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <!-- Disable default header template -->
        <record id="website.template_header_default" model="ir.ui.view">
            <field name="active" eval="False"/>
        </record>
        <!-- Default pages -->
        <!-- Disable Default Home -->
        <record id="website.homepage" model="ir.ui.view">
            <field name="active" eval="False"/>
        </record>
    </odoo>
    """

    

    template_wbuilder_opt = """<?xml version="1.0" encoding="UTF-8"?><svg id="uuid-a9541345-95cf-401e-b2c8-d4bb13d2b6f1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 234 60" width="234" height="60"><defs><clipPath id="uuid-3bcc0ef0-40a5-4efa-aa43-5e471cefb0ae"><rect x="60" y="11.54" width="114" height="36.96" fill="none" stroke-width="0"/></clipPath></defs><g clip-path="url(#uuid-3bcc0ef0-40a5-4efa-aa43-5e471cefb0ae)"><path d="M159.22,28.27c4.65.65,14.17,2.7,14.2-6.33,0-.47-.36-.34-.57-.14-5.55,5.34-7.38,0-15.28,0-6.42,0-11.85,4.29-11.85,11.95s5.19,11.95,11.85,11.95,11.85-4.06,11.85-11.95c0-1.3-.13-2.5-.41-3.59-.07-.27-.25-.33-.5-.28-.81.16-1.71.24-2.68.24-1.23,0-2.46-.12-3.64-.27-.18-.02-.37.12-.17.43.55.85.91,1.98.91,3.47,0,4.34-2.99,5.7-5.36,5.7s-5.36-1.39-5.36-5.7,3.63-5.95,7.01-5.48Z" fill="#fff" fill-rule="evenodd" stroke-width="0"/><path d="M145.73,41.82c-.25-.05-1.13-.05-1.38,0-4.22.81-1.04,6.48.69,6.48s4.91-5.67.69-6.48Z" fill="#fff" fill-rule="evenodd" stroke-width="0"/><path d="M131.02,28.27c-4.65.65-14.17,2.7-14.2-6.33,0-.47.36-.34.57-.14,5.55,5.34,7.38,0,15.28,0,6.42,0,11.85,4.29,11.85,11.95s-5.19,11.95-11.85,11.95-11.85-4.06-11.85-11.95c0-1.3.13-2.5.41-3.59.07-.27.25-.33.5-.28.81.16,1.7.24,2.68.24,1.23,0,2.46-.12,3.64-.27.18-.02.37.12.17.43-.56.85-.91,1.98-.91,3.47,0,4.34,2.99,5.7,5.36,5.7s5.36-1.39,5.36-5.7-3.62-5.95-7.01-5.48Z" fill="#fff" fill-rule="evenodd" stroke-width="0"/><path d="M118.83,33.58c0,7.44-5.3,12.12-11.96,12.12s-11.85-4.29-11.85-11.95V13.32c0-.51.45-.96.96-.96h4.63c.51,0,.96.45.96.96v11.01c2.14-2.31,5.13-2.54,6.77-2.54,7,.28,10.49,5.64,10.49,11.79ZM112.34,33.75c0-4.06-2.93-5.75-5.3-5.75s-5.47,1.41-5.47,5.7,2.93,5.81,5.3,5.81,5.47-1.69,5.47-5.75Z" fill="#fff" fill-rule="evenodd" stroke-width="0"/><path d="M88.63,19.44c-2.2,0-3.95-1.75-3.95-3.95s1.75-3.95,3.95-3.95,3.95,1.75,3.95,3.95-1.75,3.95-3.95,3.95ZM91.9,44.07c0,.51-.45.96-.96.96h-4.63c-.51,0-.96-.45-.96-.96v-20.64c0-.51.45-.96.96-.96h4.63c.51,0,.96.45.96.96v20.64Z" fill="#fff" fill-rule="evenodd" stroke-width="0"/><path d="M82.34,33.07v11c0,.51-.45.96-.96.96h-4.63c-.51,0-.96-.45-.96-.96v-11c0-2.88-1.41-5.02-4.63-5.02s-4.63,2.14-4.63,5.02v11c0,.51-.45.96-.96.96h-4.63c-.51,0-.96-.45-.96-.96v-11c0-7.5,4.91-11.28,11.17-11.28s11.17,3.78,11.17,11.28Z" fill="#fff" fill-rule="evenodd" stroke-width="0"/></g><path d="M234,0v60H0V0" fill="#aaa6d2" fill-rule="evenodd" stroke-width="0"/><path id="uuid-f13ff652-44ef-4128-930f-06fe73b2c155" d="M145.31,60l13.41-20.78-12.27-27.39h-15.83l-8.18,9.13-8.89-9.13-8.3,11.32-13.22-11.32-8.95,10.91.41-10.91h-12.86l-32.19,48.17h106.86Z" fill="#3a3a39" isolation="isolate" opacity=".12" stroke-width="0"/><path d="M126.48,11.83l-15.41,36.34h-14.82l-.59-20.63-8.18,20.63h-14.82l-1.96-36.34h12.8l-.77,22.88,9.31-22.88h12.98l.89,22.88,7.65-22.88h12.92Z" fill="#fff" stroke-width="0"/><path d="M155.59,13.67c2.49,1.19,4.39,2.9,5.75,5.1,1.3,2.19,1.96,4.68,1.96,7.53,0,1.13-.12,2.37-.3,3.62-.65,3.44-2.02,6.58-4.15,9.37-2.13,2.79-4.8,4.98-8.12,6.52-3.26,1.6-6.88,2.37-10.85,2.37h-15.83l6.7-36.34h15.83c3.5,0,6.52.59,9.01,1.84ZM147.47,35.9c1.84-1.42,2.96-3.38,3.44-5.99.12-.71.18-1.3.18-1.9,0-2.02-.65-3.56-1.96-4.62s-3.14-1.6-5.45-1.6h-2.85l-3.02,16.24h2.85c2.73-.06,4.98-.71,6.82-2.13Z" fill="#fff" stroke-width="0"/></svg>"""

    snippet_thumbnail = """<?xml version="1.0" encoding="UTF-8"?><svg id="uuid-1763626b-30ae-4377-a919-bbb8da050104" xmlns="http://www.w3.org/2000/svg" width="240" height="180" viewBox="0 0 240 180"><g id="uuid-b048a4a2-c32e-4dc6-8f93-acf0d184184d"><path d="M0,0h240v180H0V0Z" fill="#aaa6d2" fill-rule="evenodd" stroke-width="0"/></g><polygon points="169.8 59.35 143.1 59.35 129.3 74.75 114.3 59.35 100.3 78.45 78 59.35 62.9 77.75 63.6 59.35 41.9 59.35 0 122.05 0 180 142.44 180 190.5 105.55 169.8 59.35" fill="#3a3a39" isolation="isolate" opacity=".12" stroke-width="0"/><path d="M136,59.35l-26,61.3h-25l-1-34.8-13.8,34.8h-25l-3.3-61.3h21.6l-1.3,38.6,15.7-38.6h21.9l1.5,38.6,12.9-38.6h21.8Z" fill="#fff" stroke-width="0"/><path d="M185.1,62.45c4.2,2,7.4,4.9,9.7,8.6,2.2,3.7,3.3,7.9,3.3,12.7,0,1.9-.2,4-.5,6.1-1.1,5.8-3.4,11.1-7,15.8-3.6,4.7-8.1,8.4-13.7,11-5.5,2.7-11.6,4-18.3,4h-26.7l11.3-61.3h26.7c5.9,0,11,1,15.2,3.1ZM171.4,99.95c3.1-2.4,5-5.7,5.8-10.1.2-1.2.3-2.2.3-3.2,0-3.4-1.1-6-3.3-7.8s-5.3-2.7-9.2-2.7h-4.8l-5.1,27.4h4.8c4.6-.1,8.4-1.2,11.5-3.6Z" fill="#fff" stroke-width="0"/></svg>"""

    logo = """<?xml version="1.0" encoding="utf-8"?>
    <!-- Generator: Adobe Illustrator 24.3.0, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
    <svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
        viewBox="0 0 126.2 40" style="enable-background:new 0 0 126.2 40;" xml:space="preserve">
    <style type="text/css">
        .st0{fill:#8F8F8F;}
        .st1{fill:#714B67;}
    </style>
    <g id="Group_982" transform="translate(-13.729 -4.35)">
        <path id="Path_172" class="st0" d="M60.9,38c4.9,0,8.9-4,8.9-8.9c0-4.9-4-8.9-8.9-8.9c-4.9,0-8.9,4-8.9,8.9c0,0,0,0,0,0
            C51.9,34,55.9,38,60.9,38 M76.1,28.8c0.1,8.4-6.6,15.4-15,15.5c-8.4,0.1-15.4-6.6-15.5-15c0-0.2,0-0.3,0-0.5
            c0.3-8.6,7.6-15.4,16.2-15.1c2.9,0.1,5.6,1,8,2.6V7.4c0.1-1.7,1.5-3.1,3.3-3.1c1.7,0,3,1.4,3.1,3.1L76.1,28.8z M92.7,38
            c4.9,0,8.9-4,8.9-8.9c0-4.9-4-8.9-8.9-8.9c-4.9,0-8.9,4-8.9,8.9c0,0,0,0,0,0C83.8,34,87.8,38,92.7,38L92.7,38 M92.7,44.3
            c-8.4,0-15.2-6.8-15.2-15.2c0-8.4,6.8-15.2,15.2-15.2c8.4,0,15.2,6.8,15.2,15.2c0,0,0,0,0,0C108,37.4,101.2,44.3,92.7,44.3
            M124.6,38c4.9,0,8.9-4,8.9-8.9s-4-8.9-8.9-8.9c-4.9,0-8.9,4-8.9,8.9c0,0,0,0,0,0C115.7,34,119.7,38,124.6,38 M124.6,44.3
            c-8.4,0-15.2-6.8-15.2-15.2c0-8.4,6.8-15.2,15.2-15.2c8.4,0,15.2,6.8,15.2,15.2c0,0,0,0,0,0C139.9,37.4,133,44.3,124.6,44.3"/>
        <path id="Path_173" class="st1" d="M29,38c4.9,0,8.9-4,8.9-8.9c0-4.9-4-8.9-8.9-8.9c-4.9,0-8.9,4-8.9,8.9c0,0,0,0,0,0
            C20,34,24,38,29,38 M29,44.3c-8.4,0-15.2-6.8-15.2-15.2S20.5,13.8,29,13.8S44.2,20.6,44.2,29c0,0,0,0,0,0
            C44.2,37.4,37.4,44.3,29,44.3C29,44.3,29,44.3,29,44.3"/>
    </g>
    </svg>"""

    xml_example = """<?xml version="1.0" encoding="utf-8"?>
    <templates>
        <!-- If you need to call global QWeb JS templates through a global JS file (/static/src/js), this is how/where you can declare it.  -->
        <t t-name=\""""+name+""".x_wd_example">
            <!-- Your markup here -->
        </t>
    </templates>"""

    website_templates = """<?xml version="1.0" encoding="utf-8" ?>
    <odoo>
        <!-- [ CUSTOM HEADER ]-->
        <!-- =================================== -->

        <!-- [ TEMPLATE: HEADER OPT ]-->
        <template id="template_header_opt" inherit_id="website.snippet_options" name=" Scaffold Header Template - Option">
            <xpath expr="//we-select[@data-variable='header-template']" position="inside">
                <we-button 
                    title="Scaffold"
                    data-customize-website-views=\""""+name+""".header" 
                    data-customize-website-variable="'Scaffold'" 
                    data-img="/"""+name+"""/static/src/img/wbuilder/template_wbuilder_opt.svg"
                />
            </xpath>
        </template>
        <!-- [ /TEMPLATE: HEADER OPT ]-->

        <!-- [ RECORD: HEADER ]-->
        <record id="header" model="ir.ui.view">
            <field name="name">Scaffold Header</field>
            <field name="type">qweb</field>
            <field name="key">"""+name+""".header</field>
            <field name="inherit_id" ref="website.layout"/>
            <field name="mode">extension</field>
            <field name="arch" type="xml">
                <xpath expr="//header//nav" position="replace">
                    <!-- Your custom markup here -->
                    <!-- The example below used template_header_default's markup -->
                    <t t-call="website.navbar">
                        <t t-set="_navbar_classes" t-valuef="x_wd_header d-none d-lg-block shadow-sm"/>
            
                        <div id="o_main_nav" class="container">
                            <!-- Brand -->
                            <t t-call="website.placeholder_header_brand">
                                <t t-set="_link_class" t-valuef="me-4"/>
                            </t>
                            <!-- Navbar -->
                            <t t-call="website.navbar_nav">
                                <t t-set="_nav_class" t-valuef="me-auto"/>
            
                                <!-- Menu -->
                                <t t-foreach="website.menu_id.child_id" t-as="submenu">
                                    <t t-call="website.submenu">
                                        <t t-set="item_class" t-valuef="nav-item"/>
                                        <t t-set="link_class" t-valuef="nav-link"/>
                                    </t>
                                </t>
                            </t>
                            <!-- Extra elements -->
                            <ul class="navbar-nav align-items-center gap-2 flex-shrink-0 justify-content-end ps-3">
                                <!-- Search Bar -->
                                <t t-call="website.placeholder_header_search_box">
                                    <t t-set="_layout" t-valuef="modal"/>
                                    <t t-set="_input_classes" t-valuef="border border-end-0 p-3"/>
                                    <t t-set="_submit_classes" t-valuef="border border-start-0 px-4 bg-o-color-4"/>
                                    <t t-set="_button_classes" t-valuef="o_navlink_background text-reset"/>
                                </t>
                                <!-- Text element -->
                                <t t-call="website.placeholder_header_text_element"/>
                                <!-- Social -->
                                <t t-call="website.placeholder_header_social_links"/>
                                <!-- Language Selector -->
                                <t t-call="website.placeholder_header_language_selector">
                                    <t t-set="_btn_class" t-valuef="btn-outline-secondary border-0"/>
                                    <t t-set="_txt_class" t-valuef="small"/>
                                    <t t-set="_dropdown_menu_class" t-valuef="dropdown-menu-end"/>
                                </t>
                                <!-- Sign In -->
                                <t t-call="portal.placeholder_user_sign_in">
                                    <t t-set="_link_class" t-valuef="btn btn-outline-secondary"/>
                                </t>
                                <!-- User Dropdown -->
                                <t t-call="portal.user_dropdown">
                                    <t t-set="_user_name" t-value="True"/>
                                    <t t-set="_item_class" t-valuef="dropdown"/>
                                    <t t-set="_link_class" t-valuef="btn-outline-secondary border-0 fw-bold"/>
                                    <t t-set="_user_name_class" t-valuef="small"/>
                                    <t t-set="_dropdown_menu_class" t-valuef="dropdown-menu-end"/>
                                </t>
                                <!-- Call To Action -->
                                <t t-call="website.placeholder_header_call_to_action"/>
                            </ul>
                        </div>
                    </t>
                    <t t-call="website.template_header_mobile"/>
                </xpath>
            </field>
        </record>
        <!-- [ /RECORD: HEADER ]-->

        <!-- [ CUSTOM FOOTER ]-->
        <!-- =================================== -->

        <!-- [ TEMPLATE: FOOTER OPT ]-->
        <template id="template_footer_opt" inherit_id="website.snippet_options" name="Scaffold Footer Template - Option">
            <xpath expr="//we-select[@data-variable='footer-template']" position="inside">
                <we-button title="Scaffold"
                    data-customize-website-views=\""""+name+""".footer"
                    data-customize-website-variable="'Scaffold'"
                    data-img="/"""+name+"""/static/src/img/wbuilder/template_wbuilder_opt.svg"
                />
            </xpath>
        </template>
        <!-- [ /TEMPLATE: FOOTER OPT ]-->

        <!-- [ RECORD: FOOTER ]-->
        <record id="footer" model="ir.ui.view">
            <field name="name">Scaffold Footer</field>
            <field name="type">qweb</field>
            <field name="key">"""+name+""".footer</field>
            <field name="inherit_id" ref="website.layout"/>
            <field name="mode">extension</field>
            <field name="arch" type="xml">
                <xpath expr="//div[@id='footer']" position="replace">
                    <!-- Your custom markup here -->
                    <!-- The example below used footer_custom's markup -->
                    <div id="footer" class="x_wd_footer oe_structure oe_structure_solo" t-ignore="true" t-if="not no_footer">
                        <section class="s_text_block pt40 pb16" data-snippet="s_text_block" data-name="Text">
                            <div class="container">
                                <div class="row">
                                    <div class="col-lg-2 pt24 pb24">
                                        <h5 class="mb-3">Useful Links</h5>
                                        <ul class="list-unstyled">
                                            <li><a href="/">Home</a></li>
                                            <li><a href="#">About us</a></li>
                                            <li><a href="#">Products</a></li>
                                            <li><a href="#">Services</a></li>
                                            <li><a href="#">Legal</a></li>
                                            <t t-set="configurator_footer_links" t-value="[]"/>
                                            <li t-foreach="configurator_footer_links" t-as="link">
                                                <a t-att-href="link['href']" t-esc="link['text']"/>
                                            </li>
                                            <li><a href="/contactus">Contact us</a></li>
                                        </ul>
                                    </div>
                                    <div class="col-lg-5 pt24 pb24">
                                        <h5 class="mb-3">About us</h5>
                                        <p>We are a team of passionate people whose goal is to improve everyone's life through disruptive products. We build great products to solve your business problems.
                                        <br/><br/>Our products are designed for small to medium size companies willing to optimize their performance.</p>
                                    </div>
                                    <div id="connect" class="col-lg-4 offset-lg-1 pt24 pb24">
                                        <h5 class="mb-3">Connect with us</h5>
                                        <ul class="list-unstyled">
                                            <li><i class="fa fa-comment fa-fw me-2"/><span><a href="/contactus">Contact us</a></span></li>
                                            <li><i class="fa fa-envelope fa-fw me-2"/><span><a href="mailto:info@yourcompany.example.com">info@yourcompany.example.com</a></span></li>
                                            <li><i class="fa fa-phone fa-fw me-2"/><span class="o_force_ltr"><a href="tel:+1(650)555-0111">+1 (650) 555-0111</a></span></li>
                                        </ul>
                                        <div class="s_social_media text-start o_not_editable" data-snippet="s_social_media" data-name="Social Media" contenteditable="false">
                                            <h5 class="s_social_media_title d-none" contenteditable="true">Follow us</h5>
                                            <a href="/website/social/facebook" class="s_social_media_facebook" target="_blank">
                                                <i class="fa fa-facebook rounded-circle shadow-sm o_editable_media"/>
                                            </a>
                                            <a href="/website/social/twitter" class="s_social_media_twitter" target="_blank">
                                                <i class="fa fa-twitter rounded-circle shadow-sm o_editable_media"/>
                                            </a>
                                            <a href="/website/social/linkedin" class="s_social_media_linkedin" target="_blank">
                                                <i class="fa fa-linkedin rounded-circle shadow-sm o_editable_media"/>
                                            </a>
                                            <a href="/" class="text-800">
                                                <i class="fa fa-home rounded-circle shadow-sm o_editable_media"/>
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </section>
                    </div>
                </xpath>
            </field>
        </record>
        <!-- [ /RECORD: FOOTER ]-->
    </odoo>"""

    # Data
    zip_file.writestr(name+'/data/pages/home.xml',home)
    zip_file.writestr(name+'/data/menu.xml',menu)
    zip_file.writestr(name+'/data/images.xml',images)
    zip_file.writestr(name+'/data/presets.xml',presets)

    # Image
    zip_file.writestr(name+'/static/src/img/wbuilder/template_wbuilder_opt.svg',template_wbuilder_opt)
    zip_file.writestr(name+'/static/src/img/wbuilder/snippet_thumbnail.svg',snippet_thumbnail)
    zip_file.writestr(name+'/static/src/img/content/logo.svg',logo)

    # XML
    zip_file.writestr(name+'/static/src/xml/example.xml',xml_example)

    # Views
    zip_file.writestr(name+'/views/website_templates.xml',website_templates)
    
    im = 'iVBORw0KGgoAAAANSUhEUgAAA9cAAAPWCAYAAADqK2uMAAAgAElEQVR4nOzd63edV34f9ke8gAABEgBBEBRFitRIGmqoGzOeOJNJXNtxEqdebuv2Rd/0Rdy/oO1fUP8J/g/i9EW9uurVOKtO4qnjydixZY7XWKFEDUWK0lAkJd5BAMQdIKGufURoQBKXc85+nrOfy+ezFjMUSQA7FnR4vs/+7t9+4auvvsqq5K//8/W/v+Efv7fJH3kpy7JjPVwSAABA093MsuzLbX7v5oZ//vIf/crLN7f4s5X1QtnC9bn3boxkWXY2y7Jfy7Js/eensiw7mXptAAAA5OpalmWfP/n5j5/87/ksy6a//4MTP97m40onebg+996N9SC9/mM46YIAAAAoi5knYfvHT0L4+e//4MT51IvaTM/D9ZOd6d95EqR/R5gGAACgQ3/xJHD/uCw73D0L1+feuxHC9O9mWfYve/IFAQAAaIp/m2XZH4cf3//BiekUCyg8XJ9770YI1L/nzDQAAAA98G+fhOw/6OUXLSxcC9UAAAAkFM5rh4D9+9//wYnP2/jzUXIP108GlIX/D7yb6ycGAACA7vzrsPlbZMjONVyfe+/G72dZ9r/k9gkBAAAgP4WF7FzC9bn3bpx6cnjcbjUAAABlNvMkYP9+np80Olw/qYH/2JVaAAAAVEi4zut389rF3hXzwU+GlgnWAAAAVM2vZll2/tx7N34nj0/Wdbh+Eqz/lWANAABARYU8+2/OvXfj92I/UVe18CdV8P8S+8UBAACgJP71939w4ne7/eCOw3UZz1gvLz167teWNvk1AAAA8tPXtzvbteuFTX9vX/+enq8nB10H7I7C9bn3bow8CdY9mwr++NFa9ujRWissf7X2Vbay8rj16yvLwjMAAEBV9O37OmyHML63b/fXv/YknO/dJqQn0FXA7jRcF3qP9eMnIXp15XErRAvQAAAAzREC+HrYDsF7z55d3wTxHvvfOr2qq+1wfe69G7+WZdl/6nZlm1kP06HWvbi42tqZBgAAgI1C6A5hez109yhw//ff/8GJP273D7cVrp/Uwc9nWXYydnUhUC8srGYL8yutHWoAAADoxAu7Xsj27dvTOte9f//ebPeeqFumtzKTZdnZdu/BbveE+f8aG6zn51ZaP1S9AQAAiBFaz0uLq60fM1OLrXA9MLC3FbYH9u/N68uEId5/kGXZr7Xzh3fcuT733o1TT3atO54OHnap5+ZWsrnZZZVvAAAAChd2tUPQHhzqy2ti+f/8/R+c+IMdv24b4Tp8kn/ZyVcOoXpmeqlV/QYAAIAUwo72/sG+bGioL6Y6Hurhp77/gxPT2/2hbT/7k7PWbQfrtbWvsgf3F7JbXz4UrAEAAEgqbPzOziy1MmrIqmGYdheGnxyV3tZO0X3HT7Bu9uGyUA0AAEAphax6785cdvf2XDch+39/cmR6S9HhOkz8vnNrtnWI3LlqAAAAyiwM2e4yZP/edr+55Znrc+/d+N0sy/7Vdh8cdqtDqAYAAIAqCmeyh0f62zmTve3Z6+0++ne2+o1wtjqkfMEaAACAKgt18du3ZlubxzvY9uz1puH6SZf8v9vs99Zr4O6rBgAAoA7CEeeweRw2kcMQtG387la/sdXO9aa71qGPfvfOjl8MAAAAKidsIodd7Pm5LQd1nzz33o1f2+w3tgrXz/3h8MnDoW9DywAAAKirkHmnJhey6QdbHoPedPf6uXD95G7rpyrhIViHTw4AAABNMDe73KqJrz2/wbxp03uzneundq0FawAAAJpo/dquZwL28Ln3bjwXsLcN12F42bSJ4AAAADRUyMWbBOznjlJvGa7D0LK7zlgDAADQcJsE7Od2rl/46qtfhOcn562nwgeEDwyfAAAAAMiyvX27s/GJoWzXrhfCP77y/R+c+Hz9957duW7tWoepaII1AAAA/ELr6PQvpog/VQ1/NlyfXVxYzRbmt7zTCwAAABor5OXZh8vZtuF6be2rX3tgMjgAAABsaWaq1fY+u/HXngrXD+4vnDXADAAAALb3YHLh3Y3//E24/osfXR1ZWlwdTrIqAAAAqJBw/vqH//7KN9Xwb8L1g8mFs1t+FAAAAPCU2Zmlb3L0N+H68aM14RoAAADad2r9JxvPXI+kWQsAAABU0vM718+OEQcAAAC2tWm4tnMNAAAA7ftmKPjGcP3u5n8WAAAA2Mwf/eGFVgt8185/FAAAANhOK1yvJ20AAACgI3auAQAAIA/r4frUDn8OAAAAeF5rYrhwDQAAAN1r3bylFg4AAACR7FwDAABA9341E64BAAAgnlo4AAAARBKuAQAAIMIf/eGFfrVwAAAAiHN0PVyfTLwQAAAAqCy1cAAAAIgkXAMAAEAk4RoAAAAiCdcAAAAQ55RwDQAAAJF2/dEfXhhJvQgAAACoMjvXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEa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'
    zip_file.writestr(name+'/static/description/icon.png',b64decode(re.sub("data:image/jpeg;base64,", '', im)))

    im = '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DQAAAJF2/dEfXhhJvQgAAACoMjvXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEaAAAAIgnXAAAAEEm4BgAAgEjCNQAAAEQSrgEAACCScA0AAACRhGsAAACIJFwDAABAJOEa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'
    zip_file.writestr(name+'/static/src/img/content/snippets/s_wd_snippet/logo.png',b64decode(re.sub("data:image/jpeg;base64,", '', im)))

def create_scaffold():
    name = input("What is your project name? ")
    version = input("What is your project version? ")
    while len(version) < 4 :
        print("You should add the version in param like : '17.0' or '16.4' ")
        version = input("What is your project version? ")

    yes_no = ["Y","y","N","n","yes","no","YES","NO"]
    answer_with_python = input("Does your project needs python code? Y/N ")
    while answer_with_python not in yes_no:
        answer_with_python = input("You should answer Y or N, does your project needs python code? Y/N ")

    website_number = input("How many websites does your project needs? ")
    while isinstance(website_number, int) == False:
        try:
            website_number = int(website_number)
        except:
            website_number = input("Enter an integer number. How many websites does your project needs? ")

    theme_number = input("How many themes does your project needs? ")
    while isinstance(theme_number, int) == False:
        try:
            theme_number = int(theme_number)
        except:
            theme_number = input("Enter an integer number. How many themes does your project needs? ")

    zip_buffer = BytesIO()
    with ZipFile('%s.zip' % name, 'w') as zip_file:
        create_zip(zip_file, name, version, answer_with_python, website_number, theme_number)
    zip_file.close()
