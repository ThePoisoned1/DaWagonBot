from discord.ui import View
import discord
from . import utils


class EmbedPaginatorView(View):
    def __init__(self, ctx, pages, startPage=0, timeout=30):
        self.actualPage = startPage
        self.pages = pages
        self.numPages = len(pages)
        self.ctx = ctx
        super().__init__(timeout=timeout)

    async def interaction_check(self, interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message('This is not your command man', ephemeral=True)
            return False
        return True

    async def updateMsg(self, interaction):
        await interaction.response.edit_message(embed=self.pages[self.actualPage])

    @discord.ui.button(emoji='⏮')
    async def button_first_callback(self, button, interaction):
        self.actualPage = 0
        await self.updateMsg(interaction)

    @discord.ui.button(emoji='⏪')
    async def button_prev_callback(self, button, interaction):
        if self.actualPage == 0:
            self.actualPage = self.numPages-1
        else:
            self.actualPage -= 1
        await self.updateMsg(interaction)

    @discord.ui.button(emoji='⏩')
    async def button_next_callback(self, button, interaction):
        if self.actualPage == self.numPages-1:
            self.actualPage = 0
        else:
            self.actualPage += 1
        await self.updateMsg(interaction)

    @discord.ui.button(emoji='⏭')
    async def button_last_callback(self, button, interaction):
        self.actualPage = self.numPages-1
        await self.updateMsg(interaction)

    @discord.ui.button(emoji='❌')
    async def button_clear_callback(self, button, interaction):
        self.clear_items()
        await interaction.response.edit_message(view=self)
