from django.db import models
from django.core.validators import MinValueValidator

CATEGORY_DESCRIPTIONS = (  # разрешенные для пользователя категории
    # столы (модули)
    ('modul_single', 'стол диспетчера'),
    ('modul_left', 'модуль левый'),
    ('modul_right', 'модуль правый'),
    ('modul_center', 'модуль промежуточный'),
    ('modul_22_left', 'модуль левый угловой 22°'),
    ('modul_22_right', 'модуль правый угловой 22°'),
    ('modul_22_center', 'модуль угловой 22°'),
    ('modul_angle_90', 'модуль угловой 90°'),
    # экраны
    ('screen_single_45', 'экран стола 45'),
    ('screen_single_85', 'экран стола 85'),

    ('screen_left_45', 'экран левый 45'),
    ('screen_left_85', 'экран левый 85'),
    ('screen_right_45', 'экран правый 45'),
    ('screen_right_85', 'экран правый 85'),
    ('screen_center_45', 'экран промежуточный 45'),
    ('screen_center_85', 'экран промежуточный 85'),
    ('screen_angle_90_45', 'экран угловой 90° гр. 45'),
    ('screen_angle_90_85', 'экран угловой 90° гр. 85'),
    ('screen_22_center_45', 'экран угловой 22° гр. 45'),
    ('screen_22_center_85', 'экран угловой 22° гр. 85'),
    ('screen_22_left_45', 'экран левый угловой 22° гр. 45'),
    ('screen_22_left_85', 'экран левый угловой 22° гр. 85'),
    ('screen_22_right_45', 'экран правый угловой 22° гр. 45'),
    ('screen_22_right_85', 'экран правый угловой 22° гр. 85'),
    # шины монтажные
    ('schine_montage', 'шина монтажная'),
    # опциональные комплектующие (кронштейны крепления мониторов, блоки розеток и т.д.)
    ('option', 'опциональные комплектующие')
)

CATEGORY_CHOICES = tuple([(row[0], row[0]) for row in CATEGORY_DESCRIPTIONS])


class Component(models.Model):
    # основные параметры видимые пользователю
    art = models.CharField('art', max_length=30, unique=True)
    name = models.CharField('name', max_length=200)
    price = models.IntegerField('price', validators=[MinValueValidator(0)])
    value_for_select = models.CharField('value_for_select', max_length=200) # отображение в select

    # скрытые вспомогательные свойства
    category = models.CharField('category',max_length=100,choices=CATEGORY_CHOICES)
    url_image = models.URLField('url_image',blank=True)
    lens = models.IntegerField('lens',validators=[MinValueValidator(0)])
    

    def __str__(self) -> str:
        return f"{self.art} {self.name} {self.price}"