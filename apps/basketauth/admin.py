from django.contrib import admin


class ConsumerAdmin(admin.ModelAdmin):
    fields = ('name', 'key', 'secret', 'status')
    readonly_fields = ('key', 'secret')

    def save_model(self, request, obj, form, change):
        obj.status = 'accepted'
        if change is False:
            obj.generate_random_codes()
        else:
            obj.save()
