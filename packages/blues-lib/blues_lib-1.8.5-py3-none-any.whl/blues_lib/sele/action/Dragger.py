import sys,os,re
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sele.waiter.Querier import Querier

# it's a mouse event
class Dragger():
  def __init__(self,driver):
    self.__driver = driver
    self.__querier = Querier(driver)
    self.__chains = ActionChains(driver)
    self.__builder = ActionBuilder(driver)

  # == module 2 : hold and move the element == # 
  def move_to_offset(self,target_CS_WE,offset_x,offset_y,parent_CS_WE=None,timeout=5):
    '''
    Move relative to the current position
    This method has the same effect as method drag_to_offset
    Parameter:
      target_CS_WE {str|WebElement} : The element being moved
      offset_x {int} : Move some distances along the X-axis (px)
      offset_y {int} : Move some distances along the Y-axis (px)
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None
    self.__chains \
        .click_and_hold(web_element) \
        .pause(1) \
        .move_by_offset(offset_x,offset_y) \
        .pause(1) \
        .release(web_element) \
        .perform()

  def drag_in(self,draggable_target_CS_WE,droppable_target_CS_WE,timeout=5):
    '''
    Darg the draggable into the droppable
    The centers of the two elements will coincide
    Parameter:
      draggable_target_CS_WE {str|WebElement} : The element being moved
      droppable_target_CS_WE {str|WebElement} : The container element
    '''
    droppable = self.__querier.query(droppable_target_CS_WE,timeout)
    draggable = self.__querier.query(draggable_target_CS_WE,timeout)
    if droppable and draggable:
      self.__chains.drag_and_drop(draggable,droppable).perform()

  def drag_in_offset(self,draggable_target_CS_WE,droppable_target_CS_WE,offset_x,offset_y,timeout=5):
    '''
    The distance between the two elements's centers
    '''
    droppable = self.__querier.query(droppable_target_CS_WE,timeout)
    draggable = self.__querier.query(draggable_target_CS_WE,timeout)
    if droppable and draggable:
      self.__chains \
          .click_and_hold(draggable) \
          .pause(1) \
          .move_to_element_with_offset(droppable,offset_x,offset_y) \
          .pause(1) \
          .release(draggable) \
          .pause(1) \
          .perform()

  # == module 3 : drag the element == # 
  def drag_to_offset(self,target_CS_WE,offset_x,offset_y,parent_CS_WE=None,timeout=5):
    '''
    Move relative to the current position
    Parameter:
      target_CS_WE {str|WebElement} : The element being moved
      offset_x {int} : Move some distances along the X-axis (px)
      offset_y {int} : Move some distances along the Y-axis (px)
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None
    self.__chains.drag_and_drop_by_offset(web_element,offset_x,offset_y).perform()

  def drag_to(self,target_CS_WE,x,y,parent_CS_WE=None,timeout=5):
    '''
    Move to a point relative to the viewport's top left point
    Use the new feature -- ActionBuilder
    Parameter:
      target_CS_WE {str|WebElement} : The element being moved
      x {int} : the distance to viewport's left border
      y {int} : the distance to viewport's top border
    '''
    draggable = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    self.__chains.click_and_hold(draggable).perform()
    self.__builder.pointer_action.move_to_location(x,y)
    self.__builder.perform()
    self.__chains.release(draggable).perform()

  def drag_to_v0(self,target_CS_WE,x,y):
    '''
    Move relative to the viewport
    The old method by calcualte the diff disatnce between the aim point to the current point
    Parameter:
      target_CS_WE {str|WebElement} : The element being moved
      x {int} : the distance to viewport's left border
      y {int} : the distance to viewport's top border
    '''
    coordinate = self.get_coordinate(target_CS_WE)

    current_x = coordinate['left']
    current_y = coordinate['top']

    offset_x = x - current_x
    offset_y = y - current_y

    self.drag_to_offset(target_CS_WE,offset_x,offset_y)

  # == module 4 : drag element to target == # 
  def drag_in_border(self,source,target,direction='right'):
    '''
    Move to a target container's border
    @param {str} target : the target container
    @param {str} slider : the moved element
    @param {str} slider : css target_CS_WE
    '''
    # 获取容器右侧坐标
    target_coord = self.get_coordinate(target)
    source_coord = self.get_coordinate(source)

    position = self.get_border_position(source_coord,target_coord,direction)

    self.drag_to(source,*position)

  def drag_in_right(self,source,target):
    self.drag_in_border(source,target,'right')

  def drag_in_left(self,source,target):
    self.drag_in_border(source,target,'left')

  def drag_in_top(self,source,target):
    self.drag_in_border(source,target,'top')

  def drag_in_bottom(self,source,target):
    self.drag_in_border(source,target,'bottom')

  def get_border_position(self,source_coord,target_coord,direction):
    '''
    move_to calculate the postion to the element's center point, not its top left border
    '''
    x = source_coord['left'] # init x-axis position
    y = source_coord['top'] # init y-axis position
    half_width = round(source_coord['width']/2)
    half_height = round(source_coord['height']/2)

    if direction == 'left':
      x = target_coord[direction]+half_width
    elif direction == 'right':
      x = target_coord[direction]-half_width
    elif direction == 'top':
      y = target_coord[direction]+half_height
    elif direction == 'bottom':
      y = target_coord[direction]-half_height

    return (x,y)

  # == module 5 : get element coord == # 
  def get_coordinate(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    @description : get element's position and size, the positon is base on window
    @param {str} target_CS_WE : css target_CS_WE
    @returns {dict}
    '''
    coordinate = {}
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return coordinate

    coordinate['left'] = web_element.location.get('x')
    coordinate['top'] = web_element.location.get('y')
    coordinate['width'] = web_element.size.get('width')
    coordinate['height'] = web_element.size.get('height')
    coordinate['right'] = coordinate['left']+coordinate['width']
    coordinate['bottom'] = coordinate['top']+coordinate['height']
    return coordinate


