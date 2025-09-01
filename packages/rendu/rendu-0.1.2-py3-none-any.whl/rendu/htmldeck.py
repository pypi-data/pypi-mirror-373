# Copyright (c) 2025 Mattia Borsalino

import os.path as osp
import base64
from io import BytesIO


class RenduError(Exception):
    """
    Generic Rendu exception
    """
    pass

class ArgError(RenduError):
    """
    Rendu exception for wrong args passed to a method
    """
    pass

class DuplicateError(RenduError):
    """
    Rendu exception used when attempting to duplicate a  resource meant to be
    unique (e.g. title slide, slide num etc.)
    """
    pass


class HtmlSlideDeck():
    """
    Class that represents a deck of slides
    """

    def __init__(self, title, footer=None):
        """
        Parameters
        ----------
        title: str
            The report title (common to every slide)
        footer: str, optional
            If specified, a footer common to every slide
        """
        self.title = title
        self.slides = {}      # slide_num: slide_obj
        self.footer = footer
        self.raw_fnames = []  # used to avoid duplicate file names


    def add_slide(self, slide_num, title, short):
        """
        Add a slide to the report.

        Parameters
        ----------
        slide_num: int
            The slide number, must be unique within the report
        title: str
            The title to be displayed at the top of the slide
        short: str
            A short slide description to be used in report navigation widget
        
        Returns
        -------
        slide: `Slide` 
            the slide object that has been added to the slide deck

        Raises
        ------
        DuplicateError
            If a slide with the same `slide_num` was already added
        """
        if slide_num in self.slides.keys():
            raise DuplicateError("Slide #%d already_exists"%slide_num)
        self.slides[slide_num] = Slide(slide_num, title, short)
        return self.slides[slide_num]


    def add_raw_data_slide(self, slide_num, title, short, fpath, btn_label=None):
        """
        Add a slide to the report for embedding raw data.

        Parameters
        ----------
        slide_num: int
            The slide number, must be unique within the report
        title: str
            The title to be displayed at the top of the slide
        short: str
            A short slide description to be used in report navigation widget
        fpath: str
            The path of the file containing the data to be embedded.
        btn_label:
            String to be used as label placed next to the button widget
            Default: the file name (without the leading path)

        Returns
        -------
        slide: `RawDataSlide` 
            the slide object that has been added to the slide deck
        """
        if slide_num in self.slides.keys():
            raise DuplicateError("Slide #%d already_exists"%slide_num)

        fname = osp.basename(fpath)
        if fname in self.raw_fnames:
            raise DuplicateError("%s is already present in report"%fname)
        self.raw_fnames.append(fname)

        self.slides[slide_num] = RawDataSlide(len(self.slides), title, short,
                                              fpath, btn_label=btn_label)
        return self.slides[slide_num]


    def _check_slide_contiguity(self):
        if sorted(self.slides.keys()) != list(range(len(self.slides.keys()))):
            msg = 'Slide numbering should be contiguous and start from 0'
            raise RenduError(msg)


    def _to_html(self):

        # make sure we start from slide 0 and there are no holes
        # this is a current limitation of the Javascript function
        self._check_slide_contiguity()

        # Read CSS Content
        css_path = osp.join(osp.dirname(__file__), 'render', 'render_styles.css')
        if not osp.exists(css_path):
            raise RenduError('Could not find CSS file %s'%css_path)
        with open(css_path, 'r') as fh:
            css = fh.read()

        # Read CSS Content
        script_path = osp.join(osp.dirname(__file__), 'render', 'render_scripts.js')
        if not osp.exists(script_path):
            raise RenduError('Could not find script file %s'%script_path)
        with open(script_path, 'r') as fh:
            scripts = fh.read()

        html =  ('<!DOCTYPE html>\n'
                 '<html>\n'
                 '<head>\n'
                 '  <style>\n'
                 '%s\n'
                 '  </style>\n'
                 '</head>\n'
                 '<body>\n'
                 '  <div class="container wrapper">\n'
                 '    <div id="top">\n'%css)

        html +=  '      <h1>%s</h1>\n'%self.title
        html +=  '    </div>\n'

        html +=  '    <div class="wrapper">\n'

        # menubar
        html += ('      <div id="menubar">\n'
                 '        <ul id="menulist">\n')
        for k in sorted(self.slides.keys()):
            slide = self.slides[k]
            html += '          <li class="menuitem" onclick="show(%d)">%s</li>\n'%(
                                                            slide.num, slide.short)
        html += ('        </ul>\n'
                 '      </div>\n')

        # main section 
        html += '      <div id="main">\n'
        for k in sorted(self.slides.keys()):
            slide = self.slides[k]
            html += slide.main.to_html()
        html += '      </div> <!-- main -->\n'

        # notes section
        html += '      <div id="sidebar">\n'
        for k in sorted(self.slides.keys()):
            slide = self.slides[k]
            html += slide.side.to_html()
        html += ('      </div> <!-- sidebar -->\n'
                 '    </div> <!-- wrapper -->\n')
        html += '      <div id="bottom">\n'
        if self.footer:
            html += '        %s\n'%self.footer
        html += ('      </div>\n'
                 '  </div> <!-- container wrapper -->\n')
        

        html += ('  <script>\n'
                 '%s\n'    
                 '  </script>\n'%scripts)
        html += ('  </body>\n'
                 '</html>\n')
        return html
    

    def save(self, filename):
        """
        Save report to file.

        The report must have slide indexes that start from zero and are
        contiguous or it will raise an exception.

        Parameters
        ----------
        filename: str
            The full path of the output file to be generated. If the file
            already exists it will be overwritten

        Raises
        ------
        RenduError
            non-contiguous slide indexes or non-existing file/folder
        """
        with open(filename, 'w') as fh:
            fh.write(self._to_html())



class Slide():
    """
    Class that holds the content and CSS references for a generic 
    slide in HTML slide decks
    """
    def __init__(self, slide_num, title, short):
        """
        Parameters
        ----------
        slide_num: int
            The slide number
        title: str
            The slide title
        short: str
            A shorter slide title to be used for report navigation
        """
        self.num = slide_num 
        self.title = title 
        self.short = short
        self.main = SlideSection(div_id='slide_%d'%self.num,
                                      div_classes=['slide']) 
        """ The main section of the slide (see `SlideSection`) """
        self.main.add_h1(title, classes=['titleslide'])
        self.side = SlideSection(div_id='notes_%d'%self.num,
                                      div_classes=['notes'])
        """ The side section of the slide (see `SlideSection`) """



class RawDataSlide(Slide):
    """
    Specialized Slide class to be used to embed raw data files within reports.
    """

    def __init__(self, slide_num, title, short, raw_file_path, btn_label=None):
        """
        Parameters
        ----------
        slide_num: int
            The slide number
        title: str
            The slide title
        short: str
            A short slide description to be used in report navigation widget
        raw_file_path: str
            path of file containing raw data to be embedded
        btn_label: str, optional
            String to be used as label that gets placed next to the button widget
            Default: the file name (without the leading path)
        """
        super().__init__(slide_num, title, short)

        self.fpath = raw_file_path
        self.btn_label = btn_label

        fname = osp.basename(raw_file_path)
        if btn_label is None:
            btn_label = fname
        fh = open(raw_file_path, 'r')
        raw_data = fh.read()
        fh.close()

        self.main.add_html(
            '<p class="btnbox">%s</p>'
            '<button class="btnbox" onclick="save_raw(\'%s\')">Save</button>\n'
            '<div class="rawdata" id="%s" hidden>\n'
            '%s'
            '</div>\n'%(btn_label, fname, fname, raw_data))



class HtmlDivContainer():
    """
    @private
    Class that represents an HTML division.

    Objects of this class allow to fully represent a division, both in terms
    of content and CSS style classes that each HTML element within the division
    belongs to.
    """

    def __init__(self, div_classes=None, div_id=None):
        """
        Keyword Parameters:
        ------------------
        div_id: str or None
            id attribute for this division
        div_classes: list or None
            list of HTML class attributes that should be assigned to this division.
        """
        self.div_classes = div_classes 
        self.div_id = div_id
        self.content = []  # list of dicts, each holding info about an HTML item 
        self.class_map = {'h1'  : [], # {'h1'  : ["cls1", ... , "clsn"], 
                          'h2'  : [], #  'fig' : ["clsfoo', ... , "clsbar"]}
                          'h3'  : [],
                          'p'   : [],
                          'ul'  : [],
                          'ol'  : [],
                          'fig' : []}
    

    def add_figure(self, fig_path, caption=None, classes=None): 
        self.content.append({'fig' : {'path'    : fig_path,
                                      'caption' : caption,
                                      'classes' : classes}})

    def add_h1(self, txt, classes=None):
        self.content.append({'h1'     : {'txt' :txt,
                                         'classes': classes}})


    def add_h2(self, txt, classes=None):
        self.content.append({'h2'     : {'txt' :txt,
                                         'classes': classes}})


    def add_h3(self, txt, classes=None):
        self.content.append({'h3'     : {'txt' :txt,
                                         'classes': classes}})

    
    def add_p(self, txt, classes=None):
        self.content.append({'p'     : {'txt' :txt,
                                        'classes': classes}})


    def add_ul(self, li_list, classes=None):
        self.content.append({'ul': {'li_list' : li_list,
                                    'classes' : classes}})


    def add_ol(self, li_list, classes=None):
        self.content.append({'ol': {'li_list' : li_list,
                                    'classes' : classes}})


    def add_html(self, html):
        self.content.append({'html' : {'txt' : html}})


    def _encode_img(self, img_path):
        fh = open(img_path, 'rb')
        stream = BytesIO(fh.read())
        fh.close()
        
        encoded_str = base64.b64encode(stream.getvalue()).decode('utf-8')
        return encoded_str


    def _get_img_ext(self, img_path):
        root, img_ext = osp.splitext(img_path)
        img_ext = img_ext.lower()
        if img_ext in ('.jpg', '.jpeg'):
            img_ext = '.jpeg'
        elif img_ext != '.png':
            raise ArgError('File %s must be either png/jpg/jpeg'%img_path)
        return img_ext[1:]


    def _str_class(self, el_type, extra_classes=None):

        if el_type not in self.class_map:
            raise ArgError('Invalid element type %s'%el_type)
        
        cls_list = self.class_map[el_type]
        if extra_classes is not None:
            cls_list.extend(extra_classes)
        
        if len(cls_list) > 0:
            return ' class="%s"'%(' '.join(cls_list))
        else:
            return ''


    def _str_div(self):
        ret_str = ''
        if self.div_classes is not None:
            ret_str = ' class="%s"'%(' '.join(self.div_classes))
        if self.div_id is not None:
            ret_str += ' id="%s"'%self.div_id
        return ret_str

    
    def to_html(self):
        html = '<div%s>\n'%self._str_div()
        for item in self.content:
            el_type = list(item.keys())[0]
            el_props = list(item.values())[0]  # properties

            if el_type != 'html':
                cls_list = el_props['classes']

            if el_type == 'h1':
                txt = el_props['txt']
                html += '  <h1%s>%s</h1>\n'%(self._str_class('h1', cls_list), txt)

            elif el_type == 'h2':
                txt = el_props['txt']
                html += '  <h2%s>%s</h2>\n'%(self._str_class('h2', cls_list), txt)

            elif el_type == 'h3':
                txt = el_props['txt']
                html += '  <h3%s>%s</h3>\n'%(self._str_class('h3', cls_list), txt)

            elif el_type == 'p':
                txt = el_props['txt']
                html += '  <p%s>%s</p>\n'%(self._str_class('p', cls_list), txt)

            elif el_type == 'fig':
                fig_path = el_props['path']
                caption = el_props['caption']
                encoded_str = self._encode_img(fig_path)
                ext = self._get_img_ext(fig_path)
                html += '  <figure%s>\n'%self._str_class('fig', cls_list)
                html += "    <img width=100%% src='data:image/%s;base64,%s'>\n"%(
                                                              ext, encoded_str)
                if caption is not None:
                    html += '    <figcaption class="caption">%s</figcaption>\n'%caption
                html += '  </figure>\n'

            elif el_type == 'ul':
                li_list = el_props['li_list']
                html += '  <ul%s>\n'%self._str_class('ul', cls_list)
                for li in li_list:
                    html += '    <li>%s</li>\n'%li
                html += '  </ul>\n'

            elif el_type == 'ol':
                li_list = el_props['li_list']
                html += '  <ol%s>\n'%self._str_class('ol', cls_list)
                for li in li_list:
                    html += '    <li>%s</li>\n'%li
                html += '  </ol>\n'

            elif el_type == 'html':
                html += el_props['txt']

        html += '</div>\n' 
        return html


class SlideSection(HtmlDivContainer):
    """
    Class that represents either the main or side section of a slide
    """

    def add_h1(self, txt):
        """
        Add level-1 header to the slide section

        Parameters
        ----------
        txt: str
            The text of the paragraph
        """
        super().add_h1(self, txt, classes=None)


    def add_h2(self, txt):
        """
        Add level-2 header to the slide section

        Parameters
        ----------
        txt: str
            The text of the paragraph
        """
        super().add_h2(self, txt, classes=None)


    def add_h3(self, txt):
        """
        Add level-3 header to the slide section

        Parameters
        ----------
        txt: str
            The text of the paragraph
        """
        super().add_h3(self, txt, classes=None)


    def add_p(self, txt):
        """
        Add paragraph to the slide section

        Parameters
        ----------
        txt: str
            The text of the paragraph
        """
        super().add_p(txt, classes=['slidep'])


    def add_ul(self, li_list):
        """
        Add bulleted list (unsorted list) to the slide section

        Parameters
        ----------
        li_list: list of str
            A list of strings, each string being one item of the bulleted list
        """
        super().add_ul(li_list, classes=['slidelists'])


    def add_ol(self, li_list):
        """
        Add numbering list (ordered list) to the slide section

        Parameters
        ----------
        li_list: list of str
            A list of strings, each string being one item of the numbering list
        """

        super().add_ol(li_list, classes=['slidelists'])


    def add_figure(self, fig_path, caption=None): 
        """
        Add figure to the slide section (png or jpg)

        Parameters
        ----------
        fig_path: str
            The full path of the png/jpg figure to be inserted
        caption: str, optional
            The optional caption to be added to the figure
        """
        super().add_figure(fig_path, caption=caption, classes=None)

  
    def add_html(self, html):
        """
        Add a generic html block to the slide section (experimental)

        Parameters
        ----------
        html: str
            The html code to be added (no validation is performed)
        """
        super().add_html(html) 





