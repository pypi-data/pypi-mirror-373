from __future__ import annotations

from typing import (
    Any, TypeVar, Tuple, Optional,  Callable, Generic, 
    List, 
)
from functools import cached_property
from dataclasses import dataclass, replace
from syncraft.algebra import (
    Algebra, Either, Left, Right, Error
)

from syncraft.ast import (
    ParseResult, AST, Token, TokenSpec, 
    Nothing, TokenProtocol,
    Choice, Many, ChoiceKind,
    Then, ThenKind, Marked
)
from syncraft.constraint import FrozenDict
from syncraft.syntax import Syntax
from sqlglot import TokenType
import re
import rstr
from functools import lru_cache
import random

from syncraft.constraint import Bindable

T = TypeVar('T', bound=TokenProtocol)  

S = TypeVar('S', bound=Bindable)



B = TypeVar('B')


@dataclass(frozen=True)
class GenState(Bindable, Generic[T]):
    ast: Optional[ParseResult[T]] = None
    restore_pruned: bool = False
    seed: int = 0
    def map(self, f: Callable[[Any], Any]) -> GenState[T]:
        return replace(self, ast=f(self.ast))
    
    def inject(self, a: Any) -> GenState[T]:
        return self.map(lambda _: a)
    
    def fork(self, tag: Any) -> GenState[T]:
        return replace(self, seed=hash((self.seed, tag)))

    def rng(self, tag: Any = None) -> random.Random:
        return random.Random(self.seed if tag is None else hash((self.seed, tag)))



    @cached_property
    def pruned(self)->bool:
        return self.ast is None
    
    def left(self)-> GenState[T]:
        if self.ast is None:
            return self
        if isinstance(self.ast, Then) and (self.ast.kind != ThenKind.RIGHT or self.restore_pruned):
            return replace(self, ast=self.ast.left)
        return replace(self, ast=None) 

    def right(self) -> GenState[T]:
        if self.ast is None:
            return self
        if isinstance(self.ast, Then) and (self.ast.kind != ThenKind.LEFT or self.restore_pruned):
            return replace(self, ast=self.ast.right)
        return replace(self, ast=None)

    def down(self, index: int) -> GenState[T]:
        if self.ast is None:
            return self        
        match self.ast:
            case Marked(value=value):
                return replace(self, ast=value)
            case _:
                raise TypeError(f"Invalid AST type({self.ast}) for down traversal")
    
    @classmethod
    def from_ast(cls, 
                 *, 
                 ast: Optional[ParseResult[T]], 
                 seed: int = 0, 
                 restore_pruned:bool=False) -> GenState[T]:
        return cls(ast=ast, seed=seed, restore_pruned=restore_pruned)
    
@lru_cache(maxsize=None)
def token_type_from_string(token_type: Optional[TokenType], 
                           text: str, 
                           case_sensitive:bool = False)-> TokenType:
    if not isinstance(token_type, TokenType) or token_type == TokenType.VAR:
        if case_sensitive:
            for t in TokenType:
                if t.value == text:
                    return t
        else:
            text = text.lower()
            for t in TokenType:
                if t.value == text or str(t.value).lower() == text:
                    return t
        return TokenType.VAR
    return token_type


@dataclass(frozen=True)
class TokenGen(TokenSpec):

    def __str__(self) -> str:
        tt = self.token_type.name if self.token_type else ""
        txt = self.text if self.text else ""
        reg = self.regex.pattern if self.regex else ""
        return f"TokenGen({tt}, {txt}, {self.case_sensitive}, {reg})"
        
    
    def __repr__(self) -> str:
        return self.__str__()

    def gen(self) -> Token:
        text: str
        if self.text is not None:
            text = self.text
        elif self.regex is not None:
            try:
                text = rstr.xeger(self.regex)
            except Exception as e:
                # If the regex is invalid or generation fails
                text = self.regex.pattern  # fallback to pattern string
        elif self.token_type is not None:
            text = str(self.token_type.value)
        else:
            text = "VALUE"

        return Token(token_type=token_type_from_string(self.token_type, text, case_sensitive=False), text=text)        

    @staticmethod
    def from_string(string: str) -> Token:
        return Token(token_type=token_type_from_string(None, string, case_sensitive=False), text=string)


@dataclass(frozen=True)
class Generator(Algebra[ParseResult[T], GenState[T]]):  
    @classmethod
    def state(cls, ast: Optional[ParseResult[T]] = None, seed: int = 0, restore_pruned: bool = False)->GenState[T]:
        return GenState.from_ast(ast=ast, seed=seed, restore_pruned=restore_pruned)

    def flat_map(self, f: Callable[[ParseResult[T]], Algebra[B, GenState[T]]]) -> Algebra[B, GenState[T]]: 
        def flat_map_run(input: GenState[T], use_cache:bool) -> Either[Any, Tuple[B, GenState[T]]]:
            try:
                if not isinstance(input.ast, Then) or isinstance(input.ast, Nothing):
                    return Left(Error(this=self, 
                                      message=f"Expect Then got {input.ast}",
                                      state=input))
                lft = input.left() 
                match self.run(lft, use_cache=use_cache):
                    case Left(error):
                        return Left(error)
                    case Right((value, next_input)):
                        r = input.right() 
                        match f(value).run(r, use_cache):
                            case Left(e):
                                return Left(e)
                            case Right((result, next_input)):
                                return Right((result, next_input))
                raise ValueError("flat_map should always return a value or an error.")
            except Exception as e:
                return Left(Error(
                    message=str(e),
                    this=self,
                    state=input,
                    error=e
                ))
        return self.__class__(run_f = flat_map_run, name=self.name) # type: ignore


    def many(self, *, at_least: int, at_most: Optional[int]) -> Algebra[Many[ParseResult[T]], GenState[T]]:
        if at_least <=0 or (at_most is not None and at_most < at_least):
            raise ValueError(f"Invalid arguments for many: at_least={at_least}, at_most={at_most}")
        def many_run(input: GenState[T], use_cache:bool) -> Either[Any, Tuple[Many[ParseResult[T]], GenState[T]]]:
            if input.pruned:
                upper = at_most if at_most is not None else at_least + 2
                count = input.rng("many").randint(at_least, upper)
                ret: List[Any] = []
                for i in range(count):
                    forked_input = input.fork(tag=len(ret))
                    match self.run(forked_input, use_cache):
                        case Right((value, next_input)):
                            ret.append(value)
                        case Left(_):
                            pass
                return Right((Many(value=tuple(ret)), input))
            else:
                if not isinstance(input.ast, Many) or isinstance(input.ast, Nothing):
                    return Left(Error(this=self, 
                                      message=f"Expect Many got {input.ast}",
                                      state=input))
                ret = []
                for x in input.ast.value: 
                    match self.run(input.inject(x), use_cache):
                        case Right((value, next_input)):
                            ret.append(value)
                            if at_most is not None and len(ret) > at_most:
                                return Left(Error(
                                        message=f"Expected at most {at_most} matches, got {len(ret)}",
                                        this=self,
                                        state=input.inject(x)
                                    ))                             
                        case Left(e):
                            pass
                if len(ret) < at_least:
                    return Left(Error(
                        message=f"Expected at least {at_least} matches, got {len(ret)}",
                        this=self,
                        state=input.inject(x)
                    )) 
                return Right((Many(value=tuple(ret)), input))
        return self.__class__(many_run, name=f"many({self.name})")  # type: ignore
    
 
    def or_else(self, # type: ignore
                other: Algebra[ParseResult[T], GenState[T]]
                ) -> Algebra[Choice[ParseResult[T], ParseResult[T]], GenState[T]]: 
        def or_else_run(input: GenState[T], use_cache:bool) -> Either[Any, Tuple[Choice[ParseResult[T], ParseResult[T]], GenState[T]]]:
            def exec(kind: ChoiceKind | None, 
                     left: GenState[T], 
                     right: GenState[T])->Either[Any, Tuple[Choice[ParseResult[T], ParseResult[T]], GenState[T]]]:
                match kind:
                    case ChoiceKind.LEFT:
                        match self.run(left, use_cache):
                            case Right((value, next_input)):
                                return Right((Choice(kind=ChoiceKind.LEFT, value=value), next_input))
                            case Left(error):
                                return Left(error)
                    case ChoiceKind.RIGHT:
                        match other.run(right, use_cache):
                            case Right((value, next_input)):
                                return Right((Choice(kind=ChoiceKind.RIGHT, value=value), next_input))
                            case Left(error):
                                return Left(error)
                    case None:
                        match self.run(left, use_cache):
                            case Right((value, next_input)):
                                return Right((Choice(kind=ChoiceKind.LEFT, value=value), next_input))
                            case Left(error):
                                if isinstance(error, Error) and error.committed:
                                    return Left(replace(error, committed=False))
                                match other.run(left, use_cache):
                                    case Right((value, next_input)):
                                        return Right((Choice(kind=ChoiceKind.RIGHT, value=value), next_input))
                                    case Left(error):
                                        return Left(error)
                raise ValueError(f"Invalid ChoiceKind: {kind}")

            if input.pruned:
                forked_input = input.fork(tag="or_else")
                which = forked_input.rng("or_else").choice((ChoiceKind.LEFT, ChoiceKind.RIGHT))
                return exec(which, forked_input, forked_input)
            else:
                if not isinstance(input.ast, Choice) or isinstance(input.ast, Nothing):
                    return Left(Error(this=self, 
                                      message=f"Expect Choice got {input.ast}",
                                      state=input))
                else:
                    return exec(input.ast.kind, 
                                input.inject(input.ast.value), 
                                input.inject(input.ast.value))
        return self.__class__(or_else_run, name=f"or_else({self.name} | {other.name})") # type: ignore

    @classmethod
    def token(cls, 
              token_type: Optional[TokenType] = None, 
              text: Optional[str] = None, 
              case_sensitive: bool = False,
              regex: Optional[re.Pattern[str]] = None
              )-> Algebra[ParseResult[T], GenState[T]]:      
        gen = TokenGen(token_type=token_type, text=text, case_sensitive=case_sensitive, regex=regex)  
        lazy_self: Algebra[ParseResult[T], GenState[T]]
        def token_run(input: GenState[T], use_cache:bool) -> Either[Any, Tuple[ParseResult[Token], GenState[T]]]:
            if input.pruned:
                return Right((gen.gen(), input))
            else:
                current = input.ast
                if not isinstance(current, Token) or not gen.is_valid(current):
                    return Left(Error(None, 
                                      message=f"Expected a Token({gen.text}), but got {current}.", 
                                      state=input))
                return Right((current, input))
        lazy_self = cls(token_run, name=cls.__name__ + f'.token({token_type or text or regex})')  # type: ignore
        return lazy_self



def generate(syntax: Syntax[Any, Any], 
            data: Optional[ParseResult[Any]] = None, 
            seed: int = 0, 
            restore_pruned: bool = False) -> Tuple[AST, FrozenDict[str, AST]] | Tuple[Any, None]:
    from syncraft.syntax import run
    return run(syntax, Generator, False, ast=data, seed=seed, restore_pruned=restore_pruned)


    